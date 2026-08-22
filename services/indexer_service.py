from repositories.url_repository import UrlRepository
from repositories.domain_repository import DomainRepository
from services.history_service import HistoryService
from services.indexnow_service import IndexNowService
from services.settings_service import SettingsService


class IndexerService:

    def __init__(self):
        self.url_repository = UrlRepository()
        self.domain_repository = DomainRepository()
        self.history_service = HistoryService()
        self.indexnow_service = IndexNowService()
        self.settings_service = SettingsService()

    def index_url(self, url_id):

        if url_id is None:
            raise ValueError("El ID de la URL es obligatorio")

        url_record = self.url_repository.get_by_id(url_id)

        if url_record is None:
            raise ValueError("La URL no existe")

        domain = self.domain_repository.get_by_id(
            url_record.domain_id
        )

        if domain is None:
            raise ValueError(
                "El dominio asociado no existe"
            )

        if not domain.enabled:
            raise ValueError(
                "El dominio está desactivado"
            )

        if not domain.api_key:
            raise ValueError(
                "El dominio no tiene una API key configurada"
            )

        url_record.status = "PROCESANDO"
        url_record.response_code = None
        url_record.response_message = ""

        self.url_repository.update(url_record)

        self.history_service.add(
            "INDEXACION_INICIADA",
            f"Indexación iniciada: {url_record.url}"
        )

        try:

            result = self.indexnow_service.submit(
                domain.domain,
                domain.api_key,
                url_record.url
            )

            response_code = result.get("status_code")
            response_message = result.get(
                "message",
                ""
            )

            if response_code in (200, 202):

                url_record.status = "ENVIADA"
                url_record.response_code = response_code
                url_record.response_message = (
                    response_message
                    or "Solicitud aceptada por IndexNow"
                )

                self.url_repository.update(
                    url_record
                )

                self.history_service.add(
                    "INDEXACION_COMPLETADA",
                    (
                        f"URL enviada correctamente: "
                        f"{url_record.url} "
                        f"(HTTP {response_code})"
                    )
                )

                return url_record

            url_record.status = "ERROR"
            url_record.response_code = response_code
            url_record.response_message = (
                response_message
                or "IndexNow rechazó la solicitud"
            )

            self.url_repository.update(
                url_record
            )

            self.history_service.add(
                "INDEXACION_ERROR",
                (
                    f"Error indexando {url_record.url}: "
                    f"HTTP {response_code} - "
                    f"{response_message or 'sin contenido'}"
                )
            )

            return url_record

        except Exception as error:

            url_record.status = "ERROR"
            url_record.response_code = None
            url_record.response_message = str(error)

            self.url_repository.update(
                url_record
            )

            self.history_service.add(
                "INDEXACION_ERROR",
                (
                    f"Error indexando "
                    f"{url_record.url}: {error}"
                )
            )

            return url_record

    def index_pending_urls(self):

        urls = self.url_repository.get_all()

        results = []

        try:
            retries = int(
                self.settings_service.get(
                    "indexnow_retries",
                    "3"
                )
            )
        except (TypeError, ValueError):
            retries = 3

        if retries < 0:
            retries = 0

        if retries > 10:
            retries = 10

        for url_record in urls:

            if url_record.status != "PENDIENTE":
                continue

            attempts = retries + 1

            for attempt in range(1, attempts + 1):

                result = self.index_url(
                    url_record.id
                )

                results.append(result)

                if result.status == "ENVIADA":
                    break

                if attempt < attempts:

                    self.history_service.add(
                        "INDEXACION_REINTENTO",
                        (
                            f"Reintento {attempt} de {retries} "
                            f"para: {url_record.url}"
                        )
                    )

        return results
