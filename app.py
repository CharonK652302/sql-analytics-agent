import streamlit as st
import pandas as pd
import os
import sys
import time

sys.path.append(os.path.dirname(__file__))

from agent.sql_agent import generate_sql, execute_sql, explain_sql, evaluate_sql
from agent.safety_guard import is_safe
from utils.charts import auto_chart
from utils.history import save_query, load_history, clear_history
from utils.query_logger import log_query, get_query_stats
from agent.semantic_layer import SEMANTIC_LAYER

st.set_page_config(
    page_title="SQL Analytics Agent",
    page_icon="🔍",
    layout="wide"
)

# Navigation
page = st.sidebar.radio(
    "Navigation",
    ["🔍 Query", "📚 Schema Explorer", "📈 Analytics Dashboard"],
    label_visibility="collapsed"
)

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    groq_key = st.text_input(
        "Groq API Key", type="password",
        help="Get free key at console.groq.com"
    )
    if groq_key:
        os.environ["GROQ_API_KEY"] = groq_key

    st.markdown("---")
    st.header("🗄️ Database")
    db_type = st.selectbox(
        "Select Database",
        ["SQLite (Local)", "PostgreSQL"],
        help="SQLite is ready to use. PostgreSQL requires connection string."
    )
    if db_type == "PostgreSQL":
        pg_url = st.text_input(
            "PostgreSQL URL",
            placeholder="postgresql://user:password@host:5432/dbname"
        )
        if pg_url:
            os.environ["DATABASE_URL"] = pg_url
            st.success("PostgreSQL connected!")
    else:
        os.environ["DATABASE_URL"] = "sqlite:///database/ecommerce.db"
        st.success("SQLite ready ✅")

    st.markdown("---")
    st.header("📊 Database Info")
    st.markdown("""
    **Tables:**
    - 👥 customers (2,000)
    - 📦 products (500)
    - 🏪 sellers (200)
    - 🛒 orders (10,000)
    - 🚚 deliveries
    - ⭐ reviews
    """)

    st.markdown("---")
    st.header("📈 Query Stats")
    stats = get_query_stats()
    col1, col2 = st.columns(2)
    col1.metric("Total Queries", stats['total'])
    col2.metric("Success Rate",
                f"{int((stats['successful']/max(stats['total'],1))*100)}%")
    if stats['avg_latency']:
        st.metric("Avg Latency", f"{stats['avg_latency']:.0f}ms")

    st.markdown("---")
    st.header("💡 Sample Questions")
    sample_questions = [
        "Which states have highest cancellation rate?",
        "Top 5 categories by revenue",
        "Which courier has worst delivery performance?",
        "Top 10 customers by total spending",
        "Average order value by customer tier",
        "Which brands have highest rated products?",
        "Monthly revenue trend",
        "States with most platinum customers",
    ]
    for q in sample_questions:
        if st.button(q, key=q, use_container_width=True):
            st.session_state.selected_question = q
            st.rerun()

    st.markdown("---")
    if st.button("🗑️ Clear History", use_container_width=True):
        clear_history()
        st.success("History cleared!")


# ─── PAGE 1: QUERY ───────────────────────────────────────────
if page == "🔍 Query":
    st.title("🔍 SQL Analytics Agent")
    st.markdown("**Ask questions about Indian E-commerce data — powered by Groq + FAISS RAG**")
    st.markdown("---")

    question = st.text_input(
        "Ask a question:",
        value=st.session_state.get("selected_question", ""),
        placeholder="e.g. Which states have the highest cancellation rate?",
    )
    run_btn = st.button("🚀 Run Query", type="primary")

    if run_btn and question:
        if not os.environ.get("GROQ_API_KEY"):
            st.error("Please enter your Groq API key in the sidebar first.")
        else:
            with st.spinner("🔍 Retrieving relevant schema via FAISS..."):
                start_time = time.time()
                try:
                    sql, retrieved_tables = generate_sql(question)
                    safe, msg = is_safe(sql)

                    if not safe:
                        st.error(f"🚫 {msg}")
                        log_query(question, sql, [], 0, 0, success=0, error=msg)
                        st.stop()

                    columns, rows = execute_sql(sql)
                    df = pd.DataFrame(rows, columns=columns)
                    latency_ms = (time.time() - start_time) * 1000
                    evaluation = evaluate_sql(question, sql, rows)
                    log_query(question, sql, retrieved_tables, len(rows), latency_ms)
                    save_query(question, sql, len(rows))

                    st.info(f"🔍 FAISS retrieved: **{', '.join(retrieved_tables)}**")

                    tab1, tab2, tab3, tab4 = st.tabs([
                        "📊 Results", "💻 SQL Query",
                        "📝 Explanation", "🎯 Evaluation"
                    ])

                    with tab1:
                        c1, c2, c3 = st.columns(3)
                        c1.metric("Rows", len(rows))
                        c2.metric("Latency", f"{latency_ms:.0f}ms")
                        c3.metric("SQL Quality", f"{evaluation['score']}/100")
                        st.dataframe(df, use_container_width=True)
                        fig = auto_chart(columns, rows)
                        if fig:
                            st.plotly_chart(fig, use_container_width=True)
                        csv = df.to_csv(index=False)
                        st.download_button(
                            "⬇️ Download CSV", csv,
                            file_name="results.csv", mime="text/csv"
                        )

                    with tab2:
                        st.code(sql, language="sql")
                        st.caption(f"Tables used: {', '.join(retrieved_tables)}")

                    with tab3:
                        with st.spinner("Generating explanation..."):
                            explanation = explain_sql(question, sql)
                        st.info(explanation)

                    with tab4:
                        score = evaluation['score']
                        color = "green" if score >= 80 else "orange" if score >= 60 else "red"
                        st.markdown(f"### SQL Quality Score: :{color}[{score}/100]")
                        if evaluation['issues']:
                            st.warning("Issues found:")
                            for issue in evaluation['issues']:
                                st.write(f"• {issue}")
                        else:
                            st.success("No issues found!")
                        st.metric("Rows returned", evaluation['row_count'])

                except Exception as e:
                    latency_ms = (time.time() - start_time) * 1000
                    log_query(question, "", [], 0, latency_ms, success=0, error=str(e))
                    st.error(f"Error: {str(e)}")

    st.markdown("---")
    st.header("📜 Query History")
    history = load_history()
    if not history:
        st.info("No queries yet. Ask something above!")
    else:
        for i, item in enumerate(history):
            with st.expander(f"🔹 {item['question']} ({item['rows']} rows)"):
                st.code(item['sql'], language="sql")
                if st.button("▶️ Re-run", key=f"rerun_{i}"):
                    st.session_state.selected_question = item['question']
                    st.rerun()


# ─── PAGE 2: SCHEMA EXPLORER ─────────────────────────────────
elif page == "📚 Schema Explorer":
    st.title("📚 Schema Explorer")
    st.markdown("Browse all tables, columns, and business descriptions")
    st.markdown("---")

    for table_name, info in SEMANTIC_LAYER.items():
        with st.expander(f"🗂️ {table_name.upper()}", expanded=False):
            st.markdown(f"**Description:** {info['description']}")
            st.markdown(f"**Usage:** {info['usage_notes']}")
            st.markdown("**Columns:**")
            col_data = [
                {"Column": col, "Description": desc}
                for col, desc in info['columns'].items()
            ]
            st.table(pd.DataFrame(col_data))


# ─── PAGE 3: ANALYTICS DASHBOARD ─────────────────────────────
elif page == "📈 Analytics Dashboard":
    st.title("📈 Query Analytics Dashboard")
    st.markdown("Observability metrics from query_log.db")
    st.markdown("---")

    import sqlite3 as sl
    import plotly.express as px

    LOG_DB = "database/query_log.db"

    if not os.path.exists(LOG_DB):
        st.info("No queries logged yet. Run some queries first!")
    else:
        conn = sl.connect(LOG_DB)

        # Top metrics
        total = conn.execute("SELECT COUNT(*) FROM query_log").fetchone()[0]
        success = conn.execute(
            "SELECT COUNT(*) FROM query_log WHERE success=1"
        ).fetchone()[0]
        avg_lat = conn.execute(
            "SELECT AVG(latency_ms) FROM query_log WHERE success=1"
        ).fetchone()[0] or 0
        avg_rows = conn.execute(
            "SELECT AVG(row_count) FROM query_log WHERE success=1"
        ).fetchone()[0] or 0

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Queries", total)
        c2.metric("Success Rate", f"{int((success/max(total,1))*100)}%")
        c3.metric("Avg Latency", f"{avg_lat:.0f}ms")
        c4.metric("Avg Rows", f"{avg_rows:.1f}")

        st.markdown("---")

        # Latency over time
        df_lat = pd.read_sql("""
            SELECT created_at, latency_ms, success
            FROM query_log ORDER BY created_at DESC LIMIT 50
        """, conn)

        if not df_lat.empty:
            st.subheader("⚡ Latency Over Time")
            fig_lat = px.line(
                df_lat, x="created_at", y="latency_ms",
                color="success", template="plotly_white",
                title="Query Latency (ms)"
            )
            st.plotly_chart(fig_lat, use_container_width=True)

        # Most retrieved tables
        df_tables = pd.read_sql("""
            SELECT tables_used, COUNT(*) as count
            FROM query_log WHERE success=1
            GROUP BY tables_used ORDER BY count DESC LIMIT 10
        """, conn)

        if not df_tables.empty:
            st.subheader("🗂️ Most Retrieved Tables (FAISS)")
            fig_tables = px.bar(
                df_tables, x="tables_used", y="count",
                template="plotly_white",
                title="Top Retrieved Table Combinations"
            )
            st.plotly_chart(fig_tables, use_container_width=True)

        # Recent queries
        st.subheader("📋 Recent Queries")
        df_recent = pd.read_sql("""
            SELECT question, row_count, latency_ms, success, created_at
            FROM query_log ORDER BY created_at DESC LIMIT 20
        """, conn)
        st.dataframe(df_recent, use_container_width=True)

        conn.close()