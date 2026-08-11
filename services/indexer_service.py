from repositories.url_repository import UrlRepository
from services.history_service import HistoryService


class IndexerService:

    def __init__(self):
        self.url_repository = UrlRepository()
        self.history_service = HistoryService()

    def index_url(self, url_id):
        if url_id is None:
            raise ValueError("El ID de la URL es obligatorio")

        url_record = self.url_repository.get_by_id(url_id)

        if url_record is None:
            raise ValueError("La URL no existe")

        # Marcar como procesando
        url_record.status = "PROCESANDO"
        url_record.response_code = None
        url_record.response_message = ""

        self.url_repository.update(url_record)

        self.history_service.add(
            "INDEXACION_INICIADA",
            f"Indexación iniciada: {url_record.url}"
        )

        # -------------------------------------------------
        # MODO SIMULADO
        # -------------------------------------------------
        response_code = 200
        response_message = "Indexación simulada correctamente"

        url_record.status = "ENVIADA"
        url_record.response_code = response_code
        url_record.response_message = response_message

        self.url_repository.update(url_record)

        self.history_service.add(
            "INDEXACION_COMPLETADA",
            f"URL enviada correctamente: {url_record.url}"
        )

        return url_record

    def index_pending_urls(self):
        urls = self.url_repository.get_all()

        results = []

        for url_record in urls:

            if url_record.status != "PENDIENTE":
                continue

            try:
                result = self.index_url(url_record.id)
                results.append(result)

            except Exception as error:

                url_record.status = "ERROR"
                url_record.response_code = None
                url_record.response_message = str(error)

                self.url_repository.update(url_record)

                self.history_service.add(
                    "INDEXACION_ERROR",
                    f"Error indexando {url_record.url}: {error}"
                )

                results.append(url_record)

        return results
