import sqlite3
from datetime import datetime, timedelta

DB_FILE = 'memory.db'

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS memory (
            user_id TEXT,
            timestamp DATETIME,
            role TEXT,
            content TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_message(user_id, role, content):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        INSERT INTO memory (user_id, timestamp, role, content)
        VALUES (?, ?, ?, ?)
    ''', (user_id, datetime.utcnow(), role, content))
    conn.commit()
    conn.close()

def load_recent_memory(user_id, minutes=10):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    since = datetime.utcnow() - timedelta(minutes=minutes)
    c.execute('''
        SELECT role, content FROM memory
        WHERE user_id = ? AND timestamp >= ?
        ORDER BY timestamp ASC
    ''', (user_id, since))
    rows = c.fetchall()
    conn.close()
    return [{'role': row[0], 'content': row[1]} for row in rows]
