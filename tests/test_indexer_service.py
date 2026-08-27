from models.url import UrlRecord
from models.domain import Domain
from services.indexer_service import IndexerService


class FakeUrlRepository:

    def __init__(self, url_record):
        self.url_record = url_record
        self.update_calls = []

    def get_all(self):
        return [self.url_record]

    def get_by_id(self, url_id):
        if url_id == self.url_record.id:
            return self.url_record

        return None

    def update(self, url_record):
        self.update_calls.append(
            (
                url_record.id,
                url_record.status,
                url_record.response_code
            )
        )

        return True


class FakeDomainRepository:

    def __init__(self, domain):
        self.domain = domain

    def get_by_id(self, domain_id):
        if domain_id == self.domain.id:
            return self.domain

        return None


class FakeHistoryService:

    def __init__(self):
        self.entries = []

    def add(self, event_type, description):
        self.entries.append(
            (
                event_type,
                description
            )
        )


class FakeIndexNowService:

    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = 0

    def submit(self, host, key, url):
        self.calls += 1

        response = self.responses.pop(0)

        if isinstance(response, Exception):
            raise response

        return response


class FakeSettingsService:

    def __init__(self, retries):
        self.retries = retries

    def get(self, key, default=None):
        if key == "indexnow_retries":
            return str(self.retries)

        return default


def create_service(monkeypatch, responses, retries=5):

    url_record = UrlRecord(
        id=1,
        domain_id=1,
        url="https://example.com/prueba",
        status="PENDIENTE"
    )

    domain = Domain(
        id=1,
        domain="example.com",
        api_key="TEST_KEY",
        enabled=True
    )

    url_repository = FakeUrlRepository(
        url_record
    )

    domain_repository = FakeDomainRepository(
        domain
    )

    history_service = FakeHistoryService()

    indexnow_service = FakeIndexNowService(
        responses
    )

    settings_service = FakeSettingsService(
        retries
    )

    monkeypatch.setattr(
        "services.indexer_service.UrlRepository",
        lambda: url_repository
    )

    monkeypatch.setattr(
        "services.indexer_service.DomainRepository",
        lambda: domain_repository
    )

    monkeypatch.setattr(
        "services.indexer_service.HistoryService",
        lambda: history_service
    )

    monkeypatch.setattr(
        "services.indexer_service.IndexNowService",
        lambda: indexnow_service
    )

    monkeypatch.setattr(
        "services.indexer_service.SettingsService",
        lambda: settings_service
    )

    service = IndexerService()

    return (
        service,
        url_record,
        indexnow_service,
        history_service
    )


def test_index_url_success_records_history(monkeypatch):

    service, url_record, indexnow_service, history = (
        create_service(
            monkeypatch,
            [
                {
                    "status_code": 202,
                    "message": "Aceptado"
                }
            ]
        )
    )

    result = service.index_url(
        url_record.id
    )

    assert result.status == "ENVIADA"
    assert result.response_code == 202
    assert indexnow_service.calls == 1

    event_types = [
        entry[0]
        for entry in history.entries
    ]

    assert event_types == [
        "INDEXACION_INICIADA",
        "INDEXACION_COMPLETADA"
    ]


def test_index_url_http_error_records_history(monkeypatch):

    service, url_record, indexnow_service, history = (
        create_service(
            monkeypatch,
            [
                {
                    "status_code": 500,
                    "message": "Error del servidor"
                }
            ]
        )
    )

    result = service.index_url(
        url_record.id
    )

    assert result.status == "ERROR"
    assert result.response_code == 500
    assert indexnow_service.calls == 1

    event_types = [
        entry[0]
        for entry in history.entries
    ]

    assert event_types == [
        "INDEXACION_INICIADA",
        "INDEXACION_ERROR"
    ]

    assert "HTTP 500" in history.entries[-1][1]


def test_index_url_exception_records_history(monkeypatch):

    service, url_record, indexnow_service, history = (
        create_service(
            monkeypatch,
            [
                RuntimeError("Error de conexión")
            ]
        )
    )

    result = service.index_url(
        url_record.id
    )

    assert result.status == "ERROR"
    assert result.response_code is None
    assert result.response_message == "Error de conexión"
    assert indexnow_service.calls == 1

    event_types = [
        entry[0]
        for entry in history.entries
    ]

    assert event_types == [
        "INDEXACION_INICIADA",
        "INDEXACION_ERROR"
    ]

    assert "Error de conexión" in history.entries[-1][1]


def test_retries_until_success(monkeypatch):

    service, url_record, indexnow_service, history = (
        create_service(
            monkeypatch,
            [
                {
                    "status_code": 500,
                    "message": "Error 1"
                },
                {
                    "status_code": 500,
                    "message": "Error 2"
                },
                {
                    "status_code": 500,
                    "message": "Error 3"
                },
                {
                    "status_code": 202,
                    "message": "Aceptado"
                }
            ],
            retries=5
        )
    )

    results = service.index_pending_urls()

    assert len(results) == 4
    assert indexnow_service.calls == 4
    assert url_record.status == "ENVIADA"
    assert url_record.response_code == 202

    retry_entries = [
        entry
        for entry in history.entries
        if entry[0] == "INDEXACION_REINTENTO"
    ]

    assert len(retry_entries) == 3


def test_retries_stop_after_maximum(monkeypatch):

    service, url_record, indexnow_service, history = (
        create_service(
            monkeypatch,
            [
                {
                    "status_code": 500,
                    "message": "Error"
                },
                {
                    "status_code": 500,
                    "message": "Error"
                },
                {
                    "status_code": 500,
                    "message": "Error"
                },
                {
                    "status_code": 500,
                    "message": "Error"
                },
                {
                    "status_code": 500,
                    "message": "Error"
                },
                {
                    "status_code": 500,
                    "message": "Error"
                }
            ],
            retries=5
        )
    )

    results = service.index_pending_urls()

    assert len(results) == 6
    assert indexnow_service.calls == 6
    assert url_record.status == "ERROR"
    assert url_record.response_code == 500

    retry_entries = [
        entry
        for entry in history.entries
        if entry[0] == "INDEXACION_REINTENTO"
    ]

    assert len(retry_entries) == 5
