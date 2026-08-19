import sqlite3

from core.database import DB_FILE


class SettingsRepository:

    def get_connection(self):
        return sqlite3.connect(DB_FILE)

    def get(self, key, default=None):
        conn = self.get_connection()

        try:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT value
                FROM settings
                WHERE key = ?
            """, (key,))

            row = cursor.fetchone()

            if row is None:
                return default

            return row[0]

        finally:
            conn.close()

    def get_all(self):
        conn = self.get_connection()

        try:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT key, value
                FROM settings
                ORDER BY key
            """)

            return cursor.fetchall()

        finally:
            conn.close()

    def set(self, key, value):
        conn = self.get_connection()

        try:
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO settings (key, value)
                VALUES (?, ?)
                ON CONFLICT(key)
                DO UPDATE SET
                    value = excluded.value,
                    updated_at = CURRENT_TIMESTAMP
            """, (
                key,
                str(value)
            ))

            conn.commit()

            return True

        finally:
            conn.close()

    def delete(self, key):
        conn = self.get_connection()

        try:
            cursor = conn.cursor()

            cursor.execute("""
                DELETE FROM settings
                WHERE key = ?
            """, (key,))

            conn.commit()

            return cursor.rowcount > 0

        finally:
            conn.close()
