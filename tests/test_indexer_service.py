import pytest

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

def test_index_url_requires_id(monkeypatch):
    service, _, _, _ = create_service(
        monkeypatch,
        []
    )

    import pytest

    with pytest.raises(
        ValueError,
        match="El ID de la URL es obligatorio"
    ):
        service.index_url(None)


def test_index_url_missing_url(monkeypatch):
    service, _, _, _ = create_service(
        monkeypatch,
        []
    )

    with pytest.raises(
        ValueError,
        match="La URL no existe"
    ):
        service.index_url(999)


def test_index_url_missing_domain(monkeypatch):
    service, url_record, _, _ = create_service(
        monkeypatch,
        []
    )

    class MissingDomainRepository(FakeDomainRepository):

        def get_by_id(self, domain_id):
            return None

    repository = MissingDomainRepository(
        Domain(
            id=1,
            domain="example.com",
            api_key="TEST_KEY",
            enabled=True
        )
    )

    monkeypatch.setattr(
        service,
        "domain_repository",
        repository
    )

    import pytest

    with pytest.raises(
        ValueError,
        match="El dominio asociado no existe"
    ):
        service.index_url(url_record.id)


def test_index_url_disabled_domain(monkeypatch):
    service, url_record, _, _ = create_service(
        monkeypatch,
        []
    )

    service.domain_repository.domain.enabled = False

    import pytest

    with pytest.raises(
        ValueError,
        match="El dominio está desactivado"
    ):
        service.index_url(url_record.id)


def test_index_url_without_api_key(monkeypatch):
    service, url_record, _, _ = create_service(
        monkeypatch,
        []
    )

    service.domain_repository.domain.api_key = ""

    import pytest

    with pytest.raises(
        ValueError,
        match="El dominio no tiene una API key configurada"
    ):
        service.index_url(url_record.id)


def test_index_pending_urls_returns_empty_when_no_pending(monkeypatch):
    service, url_record, _, _ = create_service(
        monkeypatch,
        []
    )

    url_record.status = "ENVIADA"

    results = service.index_pending_urls()

    assert results == []


def test_index_pending_urls_invalid_retries_uses_default(monkeypatch):
    service, url_record, indexnow_service, history = create_service(
        monkeypatch,
        [
            {
                "status_code": 202,
                "message": "Aceptado"
            }
        ]
    )

    class InvalidRetriesSettings:

        def get(self, key, default=None):
            return "NO_VALIDO"

    service.settings_service = InvalidRetriesSettings()

    results = service.index_pending_urls()

    assert len(results) == 1
    assert results[0].status == "ENVIADA"
    assert indexnow_service.calls == 1


def test_index_pending_urls_negative_retries_becomes_zero(monkeypatch):
    service, url_record, indexnow_service, history = create_service(
        monkeypatch,
        [
            {
                "status_code": 500,
                "message": "Error"
            }
        ],
        retries=-5
    )

    results = service.index_pending_urls()

    assert len(results) == 1
    assert results[0].status == "ERROR"
    assert indexnow_service.calls == 1


def test_index_pending_urls_retries_are_capped_at_ten(monkeypatch):
    responses = [
        {
            "status_code": 500,
            "message": "Error"
        }
        for _ in range(11)
    ]

    service, url_record, indexnow_service, history = create_service(
        monkeypatch,
        responses,
        retries=50
    )

    results = service.index_pending_urls()

    assert len(results) == 11
    assert indexnow_service.calls == 11
    assert url_record.status == "ERROR"

    retry_entries = [
        entry
        for entry in history.entries
        if entry[0] == "INDEXACION_REINTENTO"
    ]

    assert len(retry_entries) == 10


class FakeBatchIndexNowService:

    def __init__(self, response=None, exception=None):
        self.response = response
        self.exception = exception
        self.calls = []

    def submit_batch(self, host, key, urls):
        self.calls.append(
            (
                host,
                key,
                list(urls)
            )
        )

        if self.exception is not None:
            raise self.exception

        return self.response


class FakeBatchUrlRepository:

    def __init__(self, records):
        self.records = records
        self.update_calls = []

    def get_all(self):
        return list(self.records)

    def update(self, url_record):
        self.update_calls.append(
            (
                url_record.id,
                url_record.status,
                url_record.response_code,
                url_record.response_message
            )
        )
        return True


class FakeBatchDomainRepository:

    def __init__(self, domains):
        self.domains = domains

    def get_all(self):
        return list(self.domains)


class FakeBatchHistoryService:

    def __init__(self):
        self.entries = []

    def add(self, event_type, description):
        self.entries.append(
            (
                event_type,
                description
            )
        )


def create_batch_service(
    monkeypatch,
    records,
    domains,
    response=None,
    exception=None
):
    url_repository = FakeBatchUrlRepository(
        records
    )

    domain_repository = FakeBatchDomainRepository(
        domains
    )

    history_service = FakeBatchHistoryService()

    indexnow_service = FakeBatchIndexNowService(
        response=response,
        exception=exception
    )

    class BatchSettingsService:

        def get(self, key, default=None):
            return default

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
        lambda: BatchSettingsService()
    )

    service = IndexerService()

    return (
        service,
        url_repository,
        indexnow_service,
        history_service
    )


def test_index_pending_urls_batch_success(monkeypatch):
    records = [
        UrlRecord(
            id=1,
            domain_id=1,
            url="https://example.com/uno",
            status="PENDIENTE"
        ),
        UrlRecord(
            id=2,
            domain_id=1,
            url="https://example.com/dos",
            status="PENDIENTE"
        )
    ]

    domains = [
        Domain(
            id=1,
            domain="example.com",
            api_key="TEST_KEY",
            enabled=True
        )
    ]

    (
        service,
        repository,
        indexnow_service,
        history
    ) = create_batch_service(
        monkeypatch,
        records,
        domains,
        response={
            "status_code": 202,
            "message": "Lote aceptado"
        }
    )

    results = service.index_pending_urls_batch(
        batch_size=100
    )

    assert len(results) == 2
    assert all(
        record.status == "ENVIADA"
        for record in results
    )

    assert indexnow_service.calls == [
        (
            "example.com",
            "TEST_KEY",
            [
                "https://example.com/uno",
                "https://example.com/dos"
            ]
        )
    ]

    completed = [
        entry
        for entry in history.entries
        if entry[0] == "INDEXACION_COMPLETADA"
    ]

    assert len(completed) == 2


def test_index_pending_urls_batch_respects_batch_size(monkeypatch):
    records = [
        UrlRecord(
            id=1,
            domain_id=1,
            url="https://example.com/uno",
            status="PENDIENTE"
        ),
        UrlRecord(
            id=2,
            domain_id=1,
            url="https://example.com/dos",
            status="PENDIENTE"
        ),
        UrlRecord(
            id=3,
            domain_id=1,
            url="https://example.com/tres",
            status="PENDIENTE"
        )
    ]

    domains = [
        Domain(
            id=1,
            domain="example.com",
            api_key="TEST_KEY",
            enabled=True
        )
    ]

    (
        service,
        repository,
        indexnow_service,
        history
    ) = create_batch_service(
        monkeypatch,
        records,
        domains,
        response={
            "status_code": 200,
            "message": "Aceptado"
        }
    )

    results = service.index_pending_urls_batch(
        batch_size=2
    )

    assert len(results) == 3
    assert len(indexnow_service.calls) == 2
    assert len(indexnow_service.calls[0][2]) == 2
    assert len(indexnow_service.calls[1][2]) == 1


def test_index_pending_urls_batch_invalid_batch_size(monkeypatch):
    records = []

    domains = []

    service, _, _, _ = create_batch_service(
        monkeypatch,
        records,
        domains
    )

    import pytest

    with pytest.raises(
        ValueError,
        match="El tamaño del lote debe ser mayor que cero"
    ):
        service.index_pending_urls_batch(0)


def test_index_pending_urls_batch_missing_domain(monkeypatch):
    records = [
        UrlRecord(
            id=1,
            domain_id=99,
            url="https://example.com/prueba",
            status="PENDIENTE"
        )
    ]

    (
        service,
        repository,
        indexnow_service,
        history
    ) = create_batch_service(
        monkeypatch,
        records,
        []
    )

    results = service.index_pending_urls_batch()

    assert len(results) == 1
    assert results[0].status == "ERROR"
    assert results[0].response_message == (
        "El dominio asociado no existe"
    )
    assert indexnow_service.calls == []


def test_index_pending_urls_batch_disabled_domain(monkeypatch):
    records = [
        UrlRecord(
            id=1,
            domain_id=1,
            url="https://example.com/prueba",
            status="PENDIENTE"
        )
    ]

    domains = [
        Domain(
            id=1,
            domain="example.com",
            api_key="TEST_KEY",
            enabled=False
        )
    ]

    (
        service,
        repository,
        indexnow_service,
        history
    ) = create_batch_service(
        monkeypatch,
        records,
        domains
    )

    results = service.index_pending_urls_batch()

    assert len(results) == 1
    assert results[0].status == "ERROR"
    assert results[0].response_message == (
        "El dominio está desactivado"
    )
    assert indexnow_service.calls == []


def test_index_pending_urls_batch_without_api_key(monkeypatch):
    records = [
        UrlRecord(
            id=1,
            domain_id=1,
            url="https://example.com/prueba",
            status="PENDIENTE"
        )
    ]

    domains = [
        Domain(
            id=1,
            domain="example.com",
            api_key="",
            enabled=True
        )
    ]

    (
        service,
        repository,
        indexnow_service,
        history
    ) = create_batch_service(
        monkeypatch,
        records,
        domains
    )

    results = service.index_pending_urls_batch()

    assert len(results) == 1
    assert results[0].status == "ERROR"
    assert results[0].response_message == (
        "El dominio no tiene una API key configurada"
    )
    assert indexnow_service.calls == []


def test_index_pending_urls_batch_http_error(monkeypatch):
    records = [
        UrlRecord(
            id=1,
            domain_id=1,
            url="https://example.com/prueba",
            status="PENDIENTE"
        )
    ]

    domains = [
        Domain(
            id=1,
            domain="example.com",
            api_key="TEST_KEY",
            enabled=True
        )
    ]

    (
        service,
        repository,
        indexnow_service,
        history
    ) = create_batch_service(
        monkeypatch,
        records,
        domains,
        response={
            "status_code": 500,
            "message": "Error del servidor"
        }
    )

    results = service.index_pending_urls_batch()

    assert len(results) == 1
    assert results[0].status == "ERROR"
    assert results[0].response_code == 500
    assert results[0].response_message == "Error del servidor"

    errors = [
        entry
        for entry in history.entries
        if entry[0] == "INDEXACION_ERROR"
    ]

    assert len(errors) == 1


def test_index_pending_urls_batch_exception(monkeypatch):
    records = [
        UrlRecord(
            id=1,
            domain_id=1,
            url="https://example.com/prueba",
            status="PENDIENTE"
        )
    ]

    domains = [
        Domain(
            id=1,
            domain="example.com",
            api_key="TEST_KEY",
            enabled=True
        )
    ]

    (
        service,
        repository,
        indexnow_service,
        history
    ) = create_batch_service(
        monkeypatch,
        records,
        domains,
        exception=RuntimeError("Error de conexión")
    )

    results = service.index_pending_urls_batch()

    assert len(results) == 1
    assert results[0].status == "ERROR"
    assert results[0].response_code is None
    assert results[0].response_message == "Error de conexión"

    errors = [
        entry
        for entry in history.entries
        if entry[0] == "INDEXACION_ERROR"
    ]

    assert len(errors) == 1
    assert "Error de conexión" in errors[0][1]


def test_index_pending_urls_batch_ignores_non_pending(monkeypatch):
    records = [
        UrlRecord(
            id=1,
            domain_id=1,
            url="https://example.com/enviada",
            status="ENVIADA"
        )
    ]

    domains = [
        Domain(
            id=1,
            domain="example.com",
            api_key="TEST_KEY",
            enabled=True
        )
    ]

    (
        service,
        repository,
        indexnow_service,
        history
    ) = create_batch_service(
        monkeypatch,
        records,
        domains,
        response={
            "status_code": 202,
            "message": "Aceptado"
        }
    )

    results = service.index_pending_urls_batch()

    assert results == []
    assert indexnow_service.calls == []


def test_index_pending_urls_batch_empty_returns_empty(monkeypatch):
    (
        service,
        repository,
        indexnow_service,
        history
    ) = create_batch_service(
        monkeypatch,
        [],
        []
    )

    results = service.index_pending_urls_batch()

    assert results == []
    assert indexnow_service.calls == []
