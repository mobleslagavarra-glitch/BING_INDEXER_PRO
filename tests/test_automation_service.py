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


class FakeHistoryService:

    def __init__(self):
        self.events = []

    def add(
        self,
        event_type,
        description,
        processed_count=0,
        success_count=0,
        error_count=0
    ):
        self.events.append(
            (
                event_type,
                description,
                processed_count,
                success_count,
                error_count
            )
        )

        return len(self.events)


def create_service(
    monkeypatch,
    results,
    enabled=True
):

    indexer_service = FakeIndexerService(
        results
    )

    settings_service = FakeSettingsService(
        enabled
    )

    history_service = FakeHistoryService()

    monkeypatch.setattr(
        "services.automation_service.IndexerService",
        lambda: indexer_service
    )

    monkeypatch.setattr(
        "services.automation_service.SettingsService",
        lambda: settings_service
    )

    monkeypatch.setattr(
        "services.automation_service.HistoryService",
        lambda: history_service
    )

    service = AutomationService()

    return (
        service,
        indexer_service,
        history_service
    )


def create_url(status):

    return UrlRecord(
        id=1,
        domain_id=1,
        url="https://example.com/prueba",
        status=status
    )


def test_automation_disabled(monkeypatch):

    service, indexer_service, history_service = create_service(
        monkeypatch,
        [
            create_url("ENVIADA")
        ],
        enabled=False
    )

    results = service.run()

    assert results == []
    assert indexer_service.calls == 0
    assert history_service.events == []
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

    service, indexer_service, history_service = create_service(
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

    assert len(history_service.events) == 1

    event = history_service.events[0]

    assert event[0] == "AUTOMATIZACION_EJECUTADA"

    assert event[1] == (
        "Ejecución automática de IndexNow: "
        "procesadas: 3 | "
        "correctas: 3 | "
        "errores: 0"
    )

    assert event[2] == 3
    assert event[3] == 3
    assert event[4] == 0


def test_automation_counts_errors(monkeypatch):

    results = [
        create_url("ENVIADA"),
        create_url("ERROR"),
        create_url("ERROR")
    ]

    service, indexer_service, history_service = create_service(
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

    assert len(history_service.events) == 1

    event = history_service.events[0]

    assert event[0] == "AUTOMATIZACION_EJECUTADA"

    assert event[1] == (
        "Ejecución automática de IndexNow: "
        "procesadas: 3 | "
        "correctas: 1 | "
        "errores: 2"
    )

    assert event[2] == 3
    assert event[3] == 1
    assert event[4] == 2


def test_automation_counts_mixed_results(monkeypatch):

    results = [
        create_url("ERROR"),
        create_url("ERROR"),
        create_url("ENVIADA"),
    ]

    service, indexer_service, history_service = create_service(
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

    assert len(history_service.events) == 1

    event = history_service.events[0]

    assert event[0] == "AUTOMATIZACION_EJECUTADA"

    assert event[2] == 3
    assert event[3] == 1
    assert event[4] == 2


def test_automation_without_pending_urls(monkeypatch):

    service, indexer_service, history_service = create_service(
        monkeypatch,
        []
    )

    results = service.run()

    assert results == []
    assert indexer_service.calls == 1
    assert len(history_service.events) == 1

    event = history_service.events[0]

    assert event[0] == "AUTOMATIZACION_EJECUTADA"

    assert event[1] == (
        "Ejecución automática de IndexNow: "
        "procesadas: 0 | "
        "correctas: 0 | "
        "errores: 0"
    )

    assert event[2] == 0
    assert event[3] == 0
    assert event[4] == 0

    assert service.last_run is not None
    assert service.processed_count == 0
    assert service.success_count == 0
    assert service.error_count == 0

def test_automation_blocks_concurrent_run(monkeypatch):

    service, indexer_service, history_service = create_service(
        monkeypatch,
        [
            create_url("ENVIADA")
        ]
    )

    service.is_running = True

    results = service.run()

    assert results == []
    assert indexer_service.calls == 0
    assert history_service.events == []
    assert service.is_running is True


def test_automation_releases_lock_after_error(monkeypatch):

    service, indexer_service, history_service = create_service(
        monkeypatch,
        []
    )

    def failing_index_pending_urls():
        indexer_service.calls += 1
        raise RuntimeError("Error de prueba")

    indexer_service.index_pending_urls = (
        failing_index_pending_urls
    )

    try:
        service.run()
        assert False, "Se esperaba RuntimeError"
    except RuntimeError as error:
        assert str(error) == "Error de prueba"

    assert indexer_service.calls == 1
    assert history_service.events == []
    assert service.is_running is False
