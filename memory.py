import sqlite3
import os

DB_PATH = 'memory.db'

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS memory (
                user_id TEXT,
                role TEXT,
                message TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

def save_message(user_id, role, message):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('INSERT INTO memory (user_id, role, message) VALUES (?, ?, ?)', (user_id, role, message))
        conn.commit()

def get_history(user_id, limit=10):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('''
            SELECT role, message FROM memory
            WHERE user_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (user_id, limit))
        rows = c.fetchall()
        return [{'role': row[0], 'content': row[1]} for row in reversed(rows)]
