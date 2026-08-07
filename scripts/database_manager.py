"""
Base de datos SQLite
"""

import sqlite3

from pathlib import Path


class DatabaseManager:

    def __init__(self):

        Path("database").mkdir(exist_ok=True)

        self.connection = sqlite3.connect(
            "database/bing_indexer.db"
        )

        self.cursor = self.connection.cursor()

        self.create_tables()

    def create_tables(self):

        self.cursor.execute("""

        CREATE TABLE IF NOT EXISTS urls(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            dominio TEXT,

            url TEXT,

            fecha TEXT,

            estado TEXT,

            respuesta TEXT

        )

        """)

        self.connection.commit()