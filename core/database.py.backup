import sqlite3

from core.paths import DATABASE

DB_FILE = DATABASE / "bing_indexer.db"


def initialize_database():

    conn = sqlite3.connect(DB_FILE)

    cursor = conn.cursor()

    # Tabla de dominios
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

        # Tabla de URLs
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS urls (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            domain_id INTEGER NOT NULL,

            url TEXT UNIQUE NOT NULL,

            status TEXT DEFAULT 'PENDIENTE',

            response_code INTEGER,

            response_message TEXT DEFAULT '',

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (domain_id)
                REFERENCES domains(id)
                ON DELETE CASCADE

        )
    """)

    # Tabla de historial
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS history (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            event_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            event_type TEXT NOT NULL,

            description TEXT NOT NULL

        )
    """)

    conn.commit()

    conn.close()