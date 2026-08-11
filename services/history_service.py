import sqlite3

from core.database import DB_FILE


class HistoryService:

    def get_connection(self):
        return sqlite3.connect(DB_FILE)

    def add(self, event_type, description):
        if not event_type:
            raise ValueError("El tipo de evento es obligatorio")

        if not description:
            raise ValueError("La descripción es obligatoria")

        conn = self.get_connection()

        try:
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO history (
                    event_type,
                    description
                )
                VALUES (?, ?)
            """, (
                event_type,
                description
            ))

            conn.commit()

            return cursor.lastrowid

        finally:
            conn.close()

    def get_all(self):
        conn = self.get_connection()

        try:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    id,
                    event_date,
                    event_type,
                    description
                FROM history
                ORDER BY id DESC
            """)

            return cursor.fetchall()

        finally:
            conn.close()

    def clear(self):
        conn = self.get_connection()

        try:
            cursor = conn.cursor()

            cursor.execute("DELETE FROM history")

            conn.commit()

            return cursor.rowcount

        finally:
            conn.close()
