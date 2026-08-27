from models.url import UrlRecord
from models.domain import Domain
from services.indexer_service import IndexerService


def test_indexer_service_is_available_for_manual_indexing():
    service = IndexerService()

    assert service is not None
    assert hasattr(service, "index_url")
    assert callable(service.index_url)


def test_manual_indexing_success(monkeypatch):

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

    class FakeUrlRepository:

        def get_by_id(self, url_id):
            return url_record

        def update(self, record):
            return True

    class FakeDomainRepository:

        def get_by_id(self, domain_id):
            return domain

    class FakeHistoryService:

        def __init__(self):
            self.entries = []

        def add(self, event_type, description):
            self.entries.append(
                (event_type, description)
            )

    class FakeIndexNowService:

        def submit(self, host, key, url):
            return {
                "success": True,
                "status_code": 202,
                "message": "Aceptado"
            }

    monkeypatch.setattr(
        "services.indexer_service.UrlRepository",
        lambda: FakeUrlRepository()
    )

    monkeypatch.setattr(
        "services.indexer_service.DomainRepository",
        lambda: FakeDomainRepository()
    )

    history = FakeHistoryService()

    monkeypatch.setattr(
        "services.indexer_service.HistoryService",
        lambda: history
    )

    monkeypatch.setattr(
        "services.indexer_service.IndexNowService",
        lambda: FakeIndexNowService()
    )

    service = IndexerService()

    result = service.index_url(1)

    assert result.status == "ENVIADA"
    assert result.response_code == 202
    assert result.response_message == "Aceptado"

    event_types = [
        entry[0]
        for entry in history.entries
    ]

    assert "INDEXACION_INICIADA" in event_types
    assert "INDEXACION_COMPLETADA" in event_types


def test_manual_indexing_error(monkeypatch):

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

    class FakeUrlRepository:

        def get_by_id(self, url_id):
            return url_record

        def update(self, record):
            return True

    class FakeDomainRepository:

        def get_by_id(self, domain_id):
            return domain

    class FakeHistoryService:

        def __init__(self):
            self.entries = []

        def add(self, event_type, description):
            self.entries.append(
                (event_type, description)
            )

    class FakeIndexNowService:

        def submit(self, host, key, url):
            return {
                "success": False,
                "status_code": 500,
                "message": "Error de prueba"
            }

    monkeypatch.setattr(
        "services.indexer_service.UrlRepository",
        lambda: FakeUrlRepository()
    )

    monkeypatch.setattr(
        "services.indexer_service.DomainRepository",
        lambda: FakeDomainRepository()
    )

    history = FakeHistoryService()

    monkeypatch.setattr(
        "services.indexer_service.HistoryService",
        lambda: history
    )

    monkeypatch.setattr(
        "services.indexer_service.IndexNowService",
        lambda: FakeIndexNowService()
    )

    service = IndexerService()

    result = service.index_url(1)

    assert result.status == "ERROR"
    assert result.response_code == 500
    assert result.response_message == "Error de prueba"

    event_types = [
        entry[0]
        for entry in history.entries
    ]

    assert "INDEXACION_INICIADA" in event_types
    assert "INDEXACION_ERROR" in event_types
