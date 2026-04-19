import sqlite3
import time
import os

LOG_DB = "database/query_log.db"

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
    init_logger()
    conn = sqlite3.connect(LOG_DB)
    conn.execute("""
        INSERT INTO query_log 
        (question, sql, tables_used, row_count, latency_ms, success, error)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (question, sql, str(tables_used), row_count, latency_ms, success, error))
    conn.commit()
    conn.close()

def get_query_stats():
    init_logger()
    conn = sqlite3.connect(LOG_DB)
    stats = {}
    stats['total'] = conn.execute("SELECT COUNT(*) FROM query_log").fetchone()[0]
    stats['successful'] = conn.execute("SELECT COUNT(*) FROM query_log WHERE success=1").fetchone()[0]
    stats['avg_latency'] = conn.execute("SELECT AVG(latency_ms) FROM query_log WHERE success=1").fetchone()[0]
    stats['avg_rows'] = conn.execute("SELECT AVG(row_count) FROM query_log WHERE success=1").fetchone()[0]
    conn.close()
    return stats