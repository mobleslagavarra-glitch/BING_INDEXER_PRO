import sqlite3

from core.paths import DATABASE

DB_FILE = DATABASE / "bing_indexer.db"


def initialize_database():

    conn = sqlite3.connect(DB_FILE)

    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS domains (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        domain TEXT UNIQUE NOT NULL,

        api_key TEXT,

        enabled INTEGER DEFAULT 1,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

    )
    """)

    conn.commit()

    conn.close()