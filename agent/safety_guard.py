DANGEROUS_KEYWORDS = [
    "INSERT", "UPDATE", "DELETE", "DROP", "ALTER",
    "TRUNCATE", "CREATE", "REPLACE", "MERGE"
]

def is_safe(sql: str) -> tuple[bool, str]:
    sql_upper = sql.upper()
    for keyword in DANGEROUS_KEYWORDS:
        if keyword in sql_upper:
            return False, f"Blocked: SQL contains '{keyword}' — only SELECT queries allowed."
    if not sql_upper.strip().startswith("SELECT"):
        return False, "Blocked: Only SELECT queries are allowed."
    return True, "Safe"