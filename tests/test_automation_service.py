from models.url import UrlRecord
from services.automation_service import AutomationService


class FakeIndexerService:

    def __init__(self, results):
        self.results = results
        self.calls = 0

    def index_pending_urls(self):
        self.calls += 1
        return self.results


class FakeSettingsService:

    def __init__(self, enabled):
        self.enabled = enabled

    def get(self, key, default=None):
        if key == "indexnow_auto":
            return "1" if self.enabled else "0"

        return default


def create_service(monkeypatch, results, enabled=True):

    indexer_service = FakeIndexerService(results)
    settings_service = FakeSettingsService(enabled)

    monkeypatch.setattr(
        "services.automation_service.IndexerService",
        lambda: indexer_service
    )

    monkeypatch.setattr(
        "services.automation_service.SettingsService",
        lambda: settings_service
    )

    service = AutomationService()

    return (
        service,
        indexer_service
    )


def create_url(status):

    return UrlRecord(
        id=1,
        domain_id=1,
        url="https://example.com/prueba",
        status=status
    )


def test_automation_disabled(monkeypatch):

    service, indexer_service = create_service(
        monkeypatch,
        [
            create_url("ENVIADA")
        ],
        enabled=False
    )

    results = service.run()

    assert results == []
    assert indexer_service.calls == 0
    assert service.last_run is None
    assert service.processed_count == 0
    assert service.success_count == 0
    assert service.error_count == 0


def test_automation_counts_successes(monkeypatch):

    results = [
        create_url("ENVIADA"),
        create_url("ENVIADA"),
        create_url("ENVIADA")
    ]

    service, indexer_service = create_service(
        monkeypatch,
        results
    )

    returned = service.run()

    assert returned == results
    assert indexer_service.calls == 1
    assert service.last_run is not None
    assert service.processed_count == 3
    assert service.success_count == 3
    assert service.error_count == 0


def test_automation_counts_errors(monkeypatch):

    results = [
        create_url("ENVIADA"),
        create_url("ERROR"),
        create_url("ERROR")
    ]

    service, indexer_service = create_service(
        monkeypatch,
        results
    )

    returned = service.run()

    assert returned == results
    assert indexer_service.calls == 1
    assert service.last_run is not None
    assert service.processed_count == 3
    assert service.success_count == 1
    assert service.error_count == 2
