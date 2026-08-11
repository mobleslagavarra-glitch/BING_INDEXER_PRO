from models.url import UrlRecord
from repositories.url_repository import UrlRepository
from repositories.domain_repository import DomainRepository


class UrlService:

    def __init__(self):
        self.repository = UrlRepository()
        self.domain_repository = DomainRepository()

    def get_urls(self):
        return self.repository.get_all()

    def get_url(self, url_id):
        if url_id is None:
            raise ValueError("El ID de la URL es obligatorio")

        return self.repository.get_by_id(url_id)

    def add_url(self, domain_id, url):
        if domain_id is None:
            raise ValueError("El ID del dominio es obligatorio")

        url = self._normalize_url(url)

        if not url:
            raise ValueError("La URL no puede estar vacía")

        domain = self.domain_repository.get_by_id(domain_id)

        if domain is None:
            raise ValueError("El dominio no existe")

        if self._url_exists(url):
            raise ValueError(f"La URL '{url}' ya existe")

        record = UrlRecord(
            id=None,
            domain_id=domain_id,
            url=url,
            status="PENDIENTE",
            response_code=None,
            response_message=""
        )

        return self.repository.create(record)

    def update_url(self, url_record):
        if not isinstance(url_record, UrlRecord):
            raise TypeError("Se esperaba un objeto UrlRecord")

        if url_record.id is None:
            raise ValueError("La URL debe tener un ID")

        existing = self.repository.get_by_id(url_record.id)

        if existing is None:
            raise ValueError("La URL no existe")

        domain = self.domain_repository.get_by_id(
            url_record.domain_id
        )

        if domain is None:
            raise ValueError("El dominio no existe")

        url = self._normalize_url(url_record.url)

        if not url:
            raise ValueError("La URL no puede estar vacía")

        for item in self.repository.get_all():
            if item.id != url_record.id and item.url.lower() == url.lower():
                raise ValueError(
                    f"La URL '{url}' ya existe"
                )

        url_record.url = url
        url_record.response_message = (
            url_record.response_message or ""
        )

        return self.repository.update(url_record)

    def delete_url(self, url_id):
        if url_id is None:
            raise ValueError("El ID de la URL es obligatorio")

        return self.repository.delete(url_id)

    def _url_exists(self, url):
        return any(
            item.url.lower() == url.lower()
            for item in self.repository.get_all()
        )

    @staticmethod
    def _normalize_url(url):
        if url is None:
            return ""

        url = url.strip()

        # Convertir enlaces Markdown:
        # [https://ejemplo.com](https://ejemplo.com)
        if url.startswith("[") and "](" in url and url.endswith(")"):
            cierre = url.find("](")

            if cierre > 0:
                destino = url[cierre + 2:-1].strip()

                if destino:
                    url = destino

        return url
