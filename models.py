import sqlite3
from database import get_db_connection

def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS urls (
        short_id TEXT PRIMARY KEY,
        original_url TEXT NOT NULL,
        creator_email TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        expires_at TIMESTAMP DEFAULT (DATETIME('now', '+60 days'))
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS allowed_emails (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        short_id TEXT NOT NULL,
        email TEXT NOT NULL,
        relation TEXT,
        FOREIGN KEY (short_id) REFERENCES urls (short_id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS email_verifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        short_id TEXT NOT NULL,
        email TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        expires_at TIMESTAMP DEFAULT (DATETIME('now', '+1 day')),
        FOREIGN KEY (short_id) REFERENCES urls (short_id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS access_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        short_id TEXT NOT NULL,
        accessed_by TEXT NOT NULL,
        access_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (short_id) REFERENCES urls (short_id)
    )
    """)

    conn.commit()
    conn.close()
    print("Database tables created or updated successfully!")

if __name__ == "__main__":
    create_tables()
