import sqlite3
import time
import os
import mlflow

LOG_DB = "database/query_log.db"

# ── MLflow setup ──────────────────────────────────────────────────────────────
mlflow.set_experiment("sql-analytics-agent")


def init_logger():
    conn = sqlite3.connect(LOG_DB)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS query_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT,
            sql TEXT,
            tables_used TEXT,
            row_count INTEGER,
            latency_ms REAL,
            success INTEGER,
            error TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def log_query(question, sql, tables_used, row_count, latency_ms, success=1, error=""):
    # ── SQLite logging (existing) ─────────────────────────────────────────────
    init_logger()
    conn = sqlite3.connect(LOG_DB)
    conn.execute("""
        INSERT INTO query_log 
        (question, sql, tables_used, row_count, latency_ms, success, error)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (question, sql, str(tables_used), row_count, latency_ms, success, error))
    conn.commit()
    conn.close()

    # ── MLflow logging (new) ──────────────────────────────────────────────────
    try:
        with mlflow.start_run(run_name=f"query_{int(time.time())}"):
            # Log params — what was asked and what SQL was generated
            mlflow.log_params({
                "question"    : question[:200],
                "tables_used" : str(tables_used)[:200],
                "sql_preview" : sql[:300] if sql else "",
            })
            # Log metrics — performance and quality
            mlflow.log_metrics({
                "latency_ms" : round(latency_ms, 2),
                "row_count"  : int(row_count) if row_count else 0,
                "success"    : int(success),
            })
            # Tag the run
            mlflow.set_tags({
                "project"   : "SQL Analytics Agent",
                "has_error" : "yes" if error else "no",
                "author"    : "Sai Charan Goud Kowlampet",
            })
    except Exception:
        pass  # Never break the app if MLflow fails


def get_query_stats():
    init_logger()
    conn = sqlite3.connect(LOG_DB)
    stats = {}
    stats['total']       = conn.execute("SELECT COUNT(*) FROM query_log").fetchone()[0]
    stats['successful']  = conn.execute("SELECT COUNT(*) FROM query_log WHERE success=1").fetchone()[0]
    stats['avg_latency'] = conn.execute("SELECT AVG(latency_ms) FROM query_log WHERE success=1").fetchone()[0]
    stats['avg_rows']    = conn.execute("SELECT AVG(row_count) FROM query_log WHERE success=1").fetchone()[0]
    conn.close()
    return stats