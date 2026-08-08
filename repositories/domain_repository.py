import sqlite3

from models.domain import Domain
from core.database import DB_FILE


class DomainRepository:

    def get_connection(self):
        return sqlite3.connect(DB_FILE)

    def get_all(self):
        conn = self.get_connection()

        try:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id,
                       domain,
                       api_key,
                       enabled
                FROM domains
                ORDER BY domain
            """)

            rows = cursor.fetchall()

            return [
                Domain(
                    id=row[0],
                    domain=row[1],
                    api_key=row[2] or "",
                    enabled=bool(row[3])
                )
                for row in rows
            ]

        finally:
            conn.close()

    def get_by_id(self, domain_id):
        conn = self.get_connection()

        try:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id,
                       domain,
                       api_key,
                       enabled
                FROM domains
                WHERE id = ?
            """, (domain_id,))

            row = cursor.fetchone()

            if row is None:
                return None

            return Domain(
                id=row[0],
                domain=row[1],
                api_key=row[2] or "",
                enabled=bool(row[3])
            )

        finally:
            conn.close()

    def create(self, domain):
        conn = self.get_connection()

        try:
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO domains (
                    domain,
                    api_key,
                    enabled
                )
                VALUES (?, ?, ?)
            """, (
                domain.domain,
                domain.api_key,
                int(domain.enabled)
            ))

            conn.commit()

            domain.id = cursor.lastrowid

            return domain

        finally:
            conn.close()

    def update(self, domain):
        if domain.id is None:
            raise ValueError("No se puede actualizar un dominio sin ID")

        conn = self.get_connection()

        try:
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE domains
                SET domain = ?,
                    api_key = ?,
                    enabled = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (
                domain.domain,
                domain.api_key,
                int(domain.enabled),
                domain.id
            ))

            conn.commit()

            return cursor.rowcount > 0

        finally:
            conn.close()

    def delete(self, domain_id):
        conn = self.get_connection()

        try:
            cursor = conn.cursor()

            cursor.execute("""
                DELETE FROM domains
                WHERE id = ?
            """, (domain_id,))

            conn.commit()

            return cursor.rowcount > 0

        finally:
            conn.close()