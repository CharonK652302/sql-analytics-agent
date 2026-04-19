import json
import os

HISTORY_FILE = "query_history.json"

def save_query(question: str, sql: str, row_count: int):
    history = load_history()
    entry = {
        "question": question,
        "sql": sql,
        "rows": row_count,
    }
    history.insert(0, entry)
    history = history[:10]  # Keep last 10
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

def load_history():
    if not os.path.exists(HISTORY_FILE):
        return []
    with open(HISTORY_FILE, "r") as f:
        return json.load(f)

def clear_history():
    if os.path.exists(HISTORY_FILE):
        os.remove(HISTORY_FILE)