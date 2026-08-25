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

            description TEXT NOT NULL,

            processed_count INTEGER DEFAULT 0,

            success_count INTEGER DEFAULT 0,

            error_count INTEGER DEFAULT 0

        )
    """)

    # Migración de bases de datos existentes
    cursor.execute("PRAGMA table_info(history)")

    history_columns = {
        row[1]
        for row in cursor.fetchall()
    }

    if "processed_count" not in history_columns:
        cursor.execute("""
            ALTER TABLE history
            ADD COLUMN processed_count INTEGER DEFAULT 0
        """)

    if "success_count" not in history_columns:
        cursor.execute("""
            ALTER TABLE history
            ADD COLUMN success_count INTEGER DEFAULT 0
        """)

    if "error_count" not in history_columns:
        cursor.execute("""
            ALTER TABLE history
            ADD COLUMN error_count INTEGER DEFAULT 0
        """)

    # Tabla de configuración
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            key TEXT UNIQUE NOT NULL,

            value TEXT DEFAULT '',

            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
    """)

    conn.commit()

    conn.close()
