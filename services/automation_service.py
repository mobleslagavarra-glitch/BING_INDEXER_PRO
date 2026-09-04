from datetime import datetime

from services.indexer_service import IndexerService
from services.settings_service import SettingsService
from services.history_service import HistoryService


class AutomationService:

    INTERVAL_MS = 24 * 60 * 60 * 1000

    def __init__(self):
        self.indexer_service = IndexerService()
        self.settings_service = SettingsService()
        self.history_service = HistoryService()

        self.last_run = None
        self.processed_count = 0
        self.success_count = 0
        self.error_count = 0
        self.is_running = False

    def is_enabled(self):
        value = self.settings_service.get(
            "indexnow_auto",
            "0"
        )

        return str(value) == "1"

    def run(self):

        if not self.is_enabled():
            return []

        if self.is_running:
            return []

        self.is_running = True

        try:

            results = self.indexer_service.index_all_urls_batch()

            self.last_run = datetime.now()

            self.processed_count = len(results)

            self.success_count = sum(
                1
                for result in results
                if result.status == "ENVIADA"
            )

            self.error_count = sum(
                1
                for result in results
                if result.status == "ERROR"
            )

            self.history_service.add(
                "AUTOMATIZACION_EJECUTADA",
                (
                    "Ejecución automática diaria de IndexNow: "
                    f"procesadas: {self.processed_count} | "
                    f"correctas: {self.success_count} | "
                    f"errores: {self.error_count}"
                ),
                self.processed_count,
                self.success_count,
                self.error_count
            )

            return results

        finally:
            self.is_running = False
