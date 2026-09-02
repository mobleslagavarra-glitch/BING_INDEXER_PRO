from urllib.parse import urlparse

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

        self._validate_url_domain(url, domain.domain)

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

        self._validate_url_domain(url, domain.domain)

        for item in self.repository.get_all():
            if item.id != url_record.id and item.url.lower() == url.lower():
                raise ValueError(
                    f"La URL '{url}' ya existe"
                )

        url_record.url = url

        # Al modificar una URL, debe volver a quedar pendiente
        # de indexación y limpiarse la respuesta anterior.
        url_record.status = "PENDIENTE"
        url_record.response_code = None
        url_record.response_message = ""

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

        url = str(url).strip()

        if url.startswith("[") and "](" in url:
            partes = url.split("](", 1)

            if len(partes) == 2:
                url = partes[0][1:].strip()

        return url.strip()

    @staticmethod
    def _normalize_host(host):
        if not host:
            return ""

        host = str(host).strip()

        if not host or any(char.isspace() for char in host):
            return ""

        if "://" not in host:
            host = "https://" + host

        parsed = urlparse(host)

        if not parsed.hostname:
            return ""

        hostname = parsed.hostname.lower().rstrip(".")

        if not hostname:
            return ""

        if "." not in hostname:
            return ""

        if hostname.startswith(".") or hostname.endswith("."):
            return ""

        if ".." in hostname:
            return ""

        return hostname

    @classmethod
    def _validate_url_domain(cls, url, domain):
        url_host = cls._normalize_host(url)
        domain_host = cls._normalize_host(domain)

        if not url_host:
            raise ValueError(
                "La URL no contiene un dominio válido"
            )

        if not domain_host:
            raise ValueError(
                "El dominio seleccionado no es válido"
            )

        if url_host != domain_host:
            raise ValueError(
                "La URL no pertenece al dominio seleccionado.\n\n"
                f"Dominio seleccionado: {domain_host}\n"
                f"Dominio de la URL: {url_host}"
            )
