import sys
import os
import time
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from agent.sql_agent import generate_sql, execute_sql, explain_sql, evaluate_sql
from agent.safety_guard import is_safe
from agent.semantic_layer import SEMANTIC_LAYER, get_table_description
from utils.query_logger import log_query, get_query_stats

app = FastAPI(
    title="SQL Analytics Agent API",
    description="Production REST API for natural language to SQL — powered by Groq + FAISS RAG",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    question: str
    groq_api_key: str
    explain: Optional[bool] = True
    evaluate: Optional[bool] = True

class QueryResponse(BaseModel):
    question: str
    sql: str
    tables_retrieved: list
    columns: list
    rows: list
    row_count: int
    latency_ms: float
    explanation: Optional[str] = None
    evaluation: Optional[dict] = None

@app.get("/")
def root():
    return {
        "message": "SQL Analytics Agent API",
        "version": "1.0.0",
        "endpoints": ["/query", "/schema", "/schema/{table}", "/stats", "/health"]
    }

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "database": "connected",
        "faiss_index": "loaded"
    }

@app.post("/query", response_model=QueryResponse)
def query(request: QueryRequest):
    os.environ["GROQ_API_KEY"] = request.groq_api_key
    os.environ["DATABASE_URL"] = "sqlite:///database/ecommerce.db"

    start_time = time.time()

    try:
        # Generate SQL with FAISS RAG
        sql, retrieved_tables = generate_sql(request.question)

        # Safety check
        safe, msg = is_safe(sql)
        if not safe:
            log_query(request.question, sql, [], 0, 0, success=0, error=msg)
            raise HTTPException(status_code=400, detail=msg)

        # Execute
        columns, rows = execute_sql(sql)
        latency_ms = (time.time() - start_time) * 1000

        # Optional explanation
        explanation = None
        if request.explain:
            explanation = explain_sql(request.question, sql)

        # Optional evaluation
        evaluation = None
        if request.evaluate:
            evaluation = evaluate_sql(request.question, sql, rows)

        # Log
        log_query(request.question, sql, retrieved_tables, len(rows), latency_ms)

        return QueryResponse(
            question=request.question,
            sql=sql,
            tables_retrieved=retrieved_tables,
            columns=columns,
            rows=rows,
            row_count=len(rows),
            latency_ms=round(latency_ms, 2),
            explanation=explanation,
            evaluation=evaluation
        )

    except HTTPException:
        raise
    except Exception as e:
        latency_ms = (time.time() - start_time) * 1000
        log_query(request.question, "", [], 0, latency_ms, success=0, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/schema")
def get_schema():
    schema = {}
    for table_name, info in SEMANTIC_LAYER.items():
        schema[table_name] = {
            "description": info["description"],
            "usage": info["usage_notes"],
            "columns": info["columns"]
        }
    return {"tables": schema, "total_tables": len(schema)}

@app.get("/schema/{table_name}")
def get_table_schema(table_name: str):
    if table_name not in SEMANTIC_LAYER:
        raise HTTPException(
            status_code=404,
            detail=f"Table '{table_name}' not found. Available: {list(SEMANTIC_LAYER.keys())}"
        )
    info = SEMANTIC_LAYER[table_name]
    return {
        "table": table_name,
        "description": info["description"],
        "usage": info["usage_notes"],
        "columns": info["columns"]
    }

@app.get("/stats")
def get_stats():
    stats = get_query_stats()
    return {
        "total_queries": stats['total'],
        "successful_queries": stats['successful'],
        "success_rate": f"{int((stats['successful']/max(stats['total'],1))*100)}%",
        "avg_latency_ms": round(stats['avg_latency'] or 0, 2),
        "avg_rows_returned": round(stats['avg_rows'] or 0, 2)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)