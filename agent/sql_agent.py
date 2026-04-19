import sqlite3
import os
import time
from langchain_groq import ChatGroq

DB_PATH = "database/ecommerce.db"

FEW_SHOTS = """
Examples:

Q: Which states have the highest cancellation rate?
SQL: SELECT c.state, 
     COUNT(CASE WHEN o.status='cancelled' THEN 1 END) * 100.0 / COUNT(*) as cancellation_rate,
     COUNT(*) as total_orders
     FROM orders o JOIN customers c ON o.customer_id = c.customer_id
     GROUP BY c.state ORDER BY cancellation_rate DESC LIMIT 10;

Q: Top 5 product categories by revenue
SQL: SELECT p.category, ROUND(SUM(o.amount_inr), 2) as total_revenue, COUNT(*) as orders
     FROM orders o JOIN products p ON o.product_id = p.product_id
     WHERE o.status = 'delivered'
     GROUP BY p.category ORDER BY total_revenue DESC LIMIT 5;

Q: Which courier has the worst delivery performance?
SQL: SELECT courier, 
     ROUND(AVG(actual_days - expected_days), 2) as avg_delay_days,
     COUNT(*) as total_deliveries
     FROM deliveries GROUP BY courier ORDER BY avg_delay_days DESC;

Q: Top customers by total spending
SQL: SELECT c.name, c.city, c.tier, ROUND(SUM(o.amount_inr), 2) as total_spent
     FROM orders o JOIN customers c ON o.customer_id = c.customer_id
     WHERE o.status = 'delivered'
     GROUP BY o.customer_id ORDER BY total_spent DESC LIMIT 10;

Q: Average order value by customer tier
SQL: SELECT c.tier, ROUND(AVG(o.amount_inr), 2) as avg_order_value, COUNT(*) as total_orders
     FROM orders o JOIN customers c ON o.customer_id = c.customer_id
     GROUP BY c.tier ORDER BY avg_order_value DESC;
"""

def get_llm():
    api_key = os.getenv("GROQ_API_KEY")
    return ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0,
        groq_api_key=api_key
    )

def generate_sql(question: str) -> tuple:
    from agent.schema_retriever import retrieve_relevant_tables
    relevant_schema, retrieved_tables = retrieve_relevant_tables(question, top_k=3)

    llm = get_llm()
    prompt = f"""You are an expert SQL analyst for an Indian e-commerce platform.

RELEVANT TABLES (retrieved via semantic search):
{relevant_schema}

{FEW_SHOTS}

Rules:
- Generate only SELECT statements
- Use proper JOINs when needed
- Always add LIMIT 100 if not specified
- Use amount_inr for revenue calculations
- Return ONLY the SQL query, no explanation, no markdown

Question: {question}

SQL:"""

    response = llm.invoke(prompt)
    sql = response.content.strip()
    sql = sql.replace("```sql", "").replace("```", "").strip()
    return sql, retrieved_tables

def execute_sql(sql: str):
    db_url = os.getenv("DATABASE_URL", "sqlite:///database/ecommerce.db")

    if db_url.startswith("postgresql"):
        try:
            from sqlalchemy import create_engine, text
            engine = create_engine(db_url)
            with engine.connect() as conn:
                result = conn.execute(text(sql))
                columns = list(result.keys())
                rows = [dict(zip(columns, row)) for row in result.fetchall()]
            return columns, rows
        except Exception as e:
            raise Exception(f"PostgreSQL error: {str(e)}")
    else:
        conn = sqlite3.connect("database/ecommerce.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        conn.close()
        return columns, [dict(row) for row in rows]

def explain_sql(question: str, sql: str) -> str:
    llm = get_llm()
    prompt = f"""Explain this SQL query in simple plain English in 2-3 sentences.
Be specific about what data it retrieves and why.
Question asked: {question}
SQL query: {sql}
Explanation:"""
    response = llm.invoke(prompt)
    return response.content.strip()

def evaluate_sql(question: str, sql: str, rows: list) -> dict:
    score = 100
    issues = []

    if not rows:
        score -= 40
        issues.append("Query returned no results")

    if "SELECT *" in sql.upper():
        score -= 10
        issues.append("Using SELECT * — should specify columns")

    if len(rows) == 100:
        score -= 5
        issues.append("Hit LIMIT 100 — results may be truncated")

    if "WHERE" not in sql.upper() and "GROUP BY" not in sql.upper():
        score -= 10
        issues.append("No filtering or grouping — may return raw data")

    return {
        "score": max(score, 0),
        "issues": issues,
        "row_count": len(rows)
    }