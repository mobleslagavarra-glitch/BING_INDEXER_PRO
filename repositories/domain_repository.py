import sqlite3

from models.domain import Domain

from core.database import DB_FILE


class DomainRepository:

    def get_connection(self):

        return sqlite3.connect(DB_FILE)


    def get_all(self):

        conn = self.get_connection()

        cursor = conn.cursor()

        cursor.execute("""

            SELECT id,
                   domain,
                   '',
                   1

            FROM domains

            ORDER BY domain

        """)

        rows = cursor.fetchall()

        conn.close()

        return [

            Domain(
                id=row[0],
                domain=row[1],
                api_key=row[2],
                enabled=bool(row[3])
            )

            for row in rows

        ]