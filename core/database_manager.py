import sqlite3

from core.database import DB_FILE


class DatabaseManager:

    def __init__(self):
        self.connection = sqlite3.connect(DB_FILE)

    def cursor(self):
        return self.connection.cursor()

    def commit(self):
        self.connection.commit()

    def close(self):
        self.connection.close()