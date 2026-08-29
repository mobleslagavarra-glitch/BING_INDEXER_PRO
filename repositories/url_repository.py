import sqlite3

from models.url import UrlRecord
from core.database import DB_FILE


class UrlRepository:

    def get_connection(self):
        return sqlite3.connect(DB_FILE)

    def get_all(self):
        conn = self.get_connection()

        try:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    id,
                    domain_id,
                    url,
                    status,
                    response_code,
                    response_message
                FROM urls
                ORDER BY url
            """)

            rows = cursor.fetchall()

            return [
                UrlRecord(
                    id=row[0],
                    domain_id=row[1],
                    url=row[2],
                    status=row[3],
                    response_code=row[4],
                    response_message=row[5] or "",
                )
                for row in rows
            ]

        finally:
            conn.close()

    def get_by_id(self, url_id):
        conn = self.get_connection()

        try:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    id,
                    domain_id,
                    url,
                    status,
                    response_code,
                    response_message
                FROM urls
                WHERE id = ?
            """, (url_id,))

            row = cursor.fetchone()

            if row is None:
                return None

            return UrlRecord(
                id=row[0],
                domain_id=row[1],
                url=row[2],
                status=row[3],
                response_code=row[4],
                response_message=row[5] or "",
            )

        finally:
            conn.close()

    def create(self, url_record):
        conn = self.get_connection()

        try:
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO urls (
                    domain_id,
                    url,
                    status,
                    response_code,
                    response_message
                )
                VALUES (?, ?, ?, ?, ?)
            """, (
                url_record.domain_id,
                url_record.url,
                url_record.status,
                url_record.response_code,
                url_record.response_message,
            ))

            conn.commit()

            url_record.id = cursor.lastrowid

            return url_record

        finally:
            conn.close()


    def create_many(self, records):

        if not records:
            return 0

        conn = self.get_connection()

        try:

            cursor = conn.cursor()

            cursor.executemany("""
                INSERT INTO urls (
                    domain_id,
                    url,
                    status,
                    response_code,
                    response_message
                )
                VALUES (?, ?, ?, ?, ?)
            """, records)

            conn.commit()

            return cursor.rowcount

        finally:
            conn.close()

    def update(self, url_record):
        if url_record.id is None:
            raise ValueError(
                "No se puede actualizar una URL sin ID"
            )

        conn = self.get_connection()

        try:
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE urls
                SET
                    domain_id = ?,
                    url = ?,
                    status = ?,
                    response_code = ?,
                    response_message = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (
                url_record.domain_id,
                url_record.url,
                url_record.status,
                url_record.response_code,
                url_record.response_message or "",
                url_record.id,
            ))

            conn.commit()

            return cursor.rowcount > 0

        finally:
            conn.close()

    def delete(self, url_id):
        conn = self.get_connection()

        try:
            cursor = conn.cursor()

            cursor.execute("""
                DELETE FROM urls
                WHERE id = ?
            """, (url_id,))

            conn.commit()

            return cursor.rowcount > 0

        finally:
            conn.close()