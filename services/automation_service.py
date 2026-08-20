from services.indexer_service import IndexerService
from services.settings_service import SettingsService


class AutomationService:

    INTERVAL_MS = 60000

    def __init__(self):
        self.indexer_service = IndexerService()
        self.settings_service = SettingsService()

    def is_enabled(self):
        value = self.settings_service.get(
            "indexnow_auto",
            "0"
        )

        return str(value) == "1"

    def run(self):

        if not self.is_enabled():
            return []

        return self.indexer_service.index_pending_urls()
