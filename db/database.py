import sqlite3
from datetime import datetime

DB_NAME = "audit.db"

def _conn():
    return sqlite3.connect(DB_NAME)

def create_tables():
    c = _conn()
    cur = c.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS audit_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT,
            subject TEXT,
            marks INTEGER,
            severity TEXT,
            explanation TEXT,
            created_at TEXT
        )
    """)
    c.commit()
    c.close()

def save_results(results):
    c = _conn()
    cur = c.cursor()
    for r in results:
        cur.execute("""
            INSERT INTO audit_results
            (student_id, subject, marks, severity, explanation, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            r["student_id"], r["subject"], r["marks"],
            r["severity"], r["explanation"],
            datetime.now().isoformat()
        ))
    c.commit()
    c.close()

def fetch_all_results():
    c = _conn()
    cur = c.cursor()
    cur.execute("""
        SELECT id, student_id, subject, marks, severity, explanation, created_at
        FROM audit_results
        ORDER BY created_at DESC
    """)
    rows = cur.fetchall()
    c.close()
    return rows

def delete_record(rid):
    c = _conn()
    cur = c.cursor()
    cur.execute("DELETE FROM audit_results WHERE id=?", (rid,))
    c.commit()
    c.close()

def clear_all_history():
    c = _conn()
    cur = c.cursor()
    cur.execute("DELETE FROM audit_results")
    c.commit()
    c.close()
