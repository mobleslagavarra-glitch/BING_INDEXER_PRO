from models.url import UrlRecord
from services.automation_service import AutomationService


class FakeIndexerService:

    def __init__(self, results):
        self.results = results
        self.calls = 0

    def index_pending_urls_batch(self):
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


def create_url(status, url_id=1):

    return UrlRecord(
        id=url_id,
        domain_id=1,
        url=f"https://example.com/prueba-{url_id}",
        status=status
    )


def test_interval_is_one_minute():

    assert AutomationService.INTERVAL_MS == 60000


def test_automation_enabled(monkeypatch):

    service, indexer_service, history_service = create_service(
        monkeypatch,
        [],
        enabled=True
    )

    assert service.is_enabled() is True


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
    assert service.is_running is False


def test_automation_counts_successes(monkeypatch):

    results = [
        create_url("ENVIADA", 1),
        create_url("ENVIADA", 2),
        create_url("ENVIADA", 3)
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
    assert service.is_running is False

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
        create_url("ENVIADA", 1),
        create_url("ERROR", 2),
        create_url("ERROR", 3)
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
        create_url("ERROR", 1),
        create_url("ERROR", 2),
        create_url("ENVIADA", 3),
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
    assert service.is_running is False


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

    def failing_index_pending_urls_batch():
        indexer_service.calls += 1
        raise RuntimeError("Error de prueba")

    indexer_service.index_pending_urls_batch = (
        failing_index_pending_urls_batch
    )

    try:
        service.run()
        assert False, "Se esperaba RuntimeError"
    except RuntimeError as error:
        assert str(error) == "Error de prueba"

    assert indexer_service.calls == 1
    assert history_service.events == []
    assert service.is_running is False


def test_automation_uses_batch_processing(monkeypatch):

    results = [
        create_url("ENVIADA", 1),
        create_url("ENVIADA", 2),
        create_url("ENVIADA", 3),
    ]

    service, indexer_service, history_service = create_service(
        monkeypatch,
        results
    )

    returned = service.run()

    assert returned == results
    assert indexer_service.calls == 1
    assert service.processed_count == 3
    assert service.success_count == 3
    assert service.error_count == 0


def test_automation_can_run_again_after_completion(monkeypatch):

    first_results = [
        create_url("ENVIADA", 1),
        create_url("ERROR", 2),
    ]

    service, indexer_service, history_service = create_service(
        monkeypatch,
        first_results
    )

    first = service.run()

    assert first == first_results
    assert indexer_service.calls == 1
    assert service.processed_count == 2
    assert service.success_count == 1
    assert service.error_count == 1
    assert len(history_service.events) == 1
    assert service.is_running is False

    second_results = [
        create_url("ENVIADA", 3),
        create_url("ENVIADA", 4),
        create_url("ENVIADA", 5),
    ]

    indexer_service.results = second_results

    second = service.run()

    assert second == second_results
    assert indexer_service.calls == 2
    assert service.processed_count == 3
    assert service.success_count == 3
    assert service.error_count == 0
    assert len(history_service.events) == 2
    assert service.is_running is False


def test_automation_updates_last_run(monkeypatch):

    service, indexer_service, history_service = create_service(
        monkeypatch,
        []
    )

    assert service.last_run is None

    service.run()

    first_run = service.last_run

    assert first_run is not None

    service.run()

    second_run = service.last_run

    assert second_run is not None
    assert second_run >= first_run


def test_automation_history_contains_current_counts(monkeypatch):

    results = [
        create_url("ENVIADA", 1),
        create_url("ENVIADA", 2),
        create_url("ERROR", 3),
        create_url("ERROR", 4),
    ]

    service, indexer_service, history_service = create_service(
        monkeypatch,
        results
    )

    service.run()

    assert len(history_service.events) == 1

    event = history_service.events[0]

    assert event[0] == "AUTOMATIZACION_EJECUTADA"
    assert "procesadas: 4" in event[1]
    assert "correctas: 2" in event[1]
    assert "errores: 2" in event[1]
    assert event[2:] == (4, 2, 2)


def test_disabled_automation_preserves_previous_statistics(
    monkeypatch
):

    service, indexer_service, history_service = create_service(
        monkeypatch,
        [
            create_url("ENVIADA", 1),
            create_url("ERROR", 2),
        ],
        enabled=True
    )

    service.run()

    previous_last_run = service.last_run
    previous_processed = service.processed_count
    previous_success = service.success_count
    previous_errors = service.error_count
    previous_events = len(history_service.events)

    indexer_service.results = [
        create_url("ENVIADA", 3),
    ]

    service.settings_service.enabled = False

    result = service.run()

    assert result == []
    assert indexer_service.calls == 1
    assert service.last_run == previous_last_run
    assert service.processed_count == previous_processed
    assert service.success_count == previous_success
    assert service.error_count == previous_errors
    assert len(history_service.events) == previous_events


def test_automation_unknown_status_is_not_success_or_error(
    monkeypatch
):

    results = [
        create_url("PROCESANDO", 1),
        create_url("PENDIENTE", 2),
        create_url("OTRO", 3),
    ]

    service, indexer_service, history_service = create_service(
        monkeypatch,
        results
    )

    returned = service.run()

    assert returned == results
    assert service.processed_count == 3
    assert service.success_count == 0
    assert service.error_count == 0
    assert len(history_service.events) == 1


def test_automation_lock_is_released_after_success(monkeypatch):

    service, indexer_service, history_service = create_service(
        monkeypatch,
        [
            create_url("ENVIADA")
        ]
    )

    assert service.is_running is False

    service.run()

    assert service.is_running is False
    assert indexer_service.calls == 1
