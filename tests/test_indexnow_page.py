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

from PySide6.QtWidgets import QApplication


def get_qapplication():
    app = QApplication.instance()

    if app is None:
        app = QApplication([])

    return app


def test_indexnow_page_creates_ui(monkeypatch):

    class FakeUrlService:

        def get_urls(self):
            return []

    class FakeDomainService:

        def get_domains(self):
            return []

    class FakeIndexerService:
        pass

    monkeypatch.setattr(
        "gui.pages.indexnow.UrlService",
        lambda: FakeUrlService()
    )

    monkeypatch.setattr(
        "gui.pages.indexnow.DomainService",
        lambda: FakeDomainService()
    )

    monkeypatch.setattr(
        "gui.pages.indexnow.IndexerService",
        lambda: FakeIndexerService()
    )

    from gui.pages.indexnow import IndexNowPage

    app = get_qapplication()
    page = IndexNowPage()

    assert page.table.columnCount() == 5
    assert page.table.horizontalHeaderItem(0).text() == "ID"
    assert page.table.horizontalHeaderItem(1).text() == "Dominio"
    assert page.table.horizontalHeaderItem(2).text() == "URL"
    assert page.table.horizontalHeaderItem(3).text() == "Estado"
    assert page.table.horizontalHeaderItem(4).text() == "Código"

    assert page.send_button.text() == "Enviar a IndexNow"
    assert page.refresh_button.text() == "Actualizar"

    page.close()
    app.processEvents()


def test_indexnow_page_loads_only_valid_urls(monkeypatch):

    urls = [
        UrlRecord(
            id=1,
            domain_id=1,
            url="https://example.com/uno",
            status="PENDIENTE"
        ),
        UrlRecord(
            id=2,
            domain_id=2,
            url="https://disabled.com/dos",
            status="PENDIENTE"
        ),
        UrlRecord(
            id=3,
            domain_id=3,
            url="https://nokey.com/tres",
            status="PENDIENTE"
        ),
        UrlRecord(
            id=4,
            domain_id=99,
            url="https://missing.com/cuatro",
            status="PENDIENTE"
        ),
    ]

    domains = [
        Domain(
            id=1,
            domain="example.com",
            api_key="TEST_KEY",
            enabled=True
        ),
        Domain(
            id=2,
            domain="disabled.com",
            api_key="TEST_KEY",
            enabled=False
        ),
        Domain(
            id=3,
            domain="nokey.com",
            api_key="",
            enabled=True
        ),
    ]

    class FakeUrlService:

        def get_urls(self):
            return urls

    class FakeDomainService:

        def get_domains(self):
            return domains

    class FakeIndexerService:
        pass

    monkeypatch.setattr(
        "gui.pages.indexnow.UrlService",
        lambda: FakeUrlService()
    )

    monkeypatch.setattr(
        "gui.pages.indexnow.DomainService",
        lambda: FakeDomainService()
    )

    monkeypatch.setattr(
        "gui.pages.indexnow.IndexerService",
        lambda: FakeIndexerService()
    )

    from gui.pages.indexnow import IndexNowPage

    app = get_qapplication()
    page = IndexNowPage()

    assert page.table.rowCount() == 1
    assert page.table.item(0, 0).text() == "1"
    assert page.table.item(0, 1).text() == "example.com"
    assert page.table.item(0, 2).text() == "https://example.com/uno"
    assert page.table.item(0, 3).text() == "PENDIENTE"
    assert page.send_button.isEnabled() is True

    page.close()
    app.processEvents()


def test_indexnow_page_disables_send_button_without_urls(monkeypatch):

    class FakeUrlService:

        def get_urls(self):
            return []

    class FakeDomainService:

        def get_domains(self):
            return []

    class FakeIndexerService:
        pass

    monkeypatch.setattr(
        "gui.pages.indexnow.UrlService",
        lambda: FakeUrlService()
    )

    monkeypatch.setattr(
        "gui.pages.indexnow.DomainService",
        lambda: FakeDomainService()
    )

    monkeypatch.setattr(
        "gui.pages.indexnow.IndexerService",
        lambda: FakeIndexerService()
    )

    from gui.pages.indexnow import IndexNowPage

    app = get_qapplication()
    page = IndexNowPage()

    assert page.table.rowCount() == 0
    assert page.send_button.isEnabled() is False

    page.close()
    app.processEvents()


def test_indexnow_page_warning_without_selection(monkeypatch):

    class FakeUrlService:

        def get_urls(self):
            return []

    class FakeDomainService:

        def get_domains(self):
            return []

    class FakeIndexerService:
        pass

    monkeypatch.setattr(
        "gui.pages.indexnow.UrlService",
        lambda: FakeUrlService()
    )

    monkeypatch.setattr(
        "gui.pages.indexnow.DomainService",
        lambda: FakeDomainService()
    )

    monkeypatch.setattr(
        "gui.pages.indexnow.IndexerService",
        lambda: FakeIndexerService()
    )

    messages = []

    monkeypatch.setattr(
        "gui.pages.indexnow.QMessageBox.warning",
        lambda *args: messages.append(args)
    )

    from gui.pages.indexnow import IndexNowPage

    app = get_qapplication()
    page = IndexNowPage()

    page.send_selected_url()

    assert len(messages) == 1
    assert messages[0][1] == "IndexNow"
    assert (
        messages[0][2]
        == "Selecciona una URL para enviarla a IndexNow."
    )

    page.close()
    app.processEvents()


def test_indexnow_page_manual_send_success(monkeypatch):

    url_record = UrlRecord(
        id=1,
        domain_id=1,
        url="https://example.com/prueba",
        status="PENDIENTE"
    )

    class FakeUrlService:

        def get_urls(self):
            return [url_record]

        def get_url(self, url_id):
            return url_record

    class FakeDomainService:

        def get_domains(self):
            return [
                Domain(
                    id=1,
                    domain="example.com",
                    api_key="TEST_KEY",
                    enabled=True
                )
            ]

    class FakeResult:

        status = "ENVIADA"
        url = "https://example.com/prueba"
        response_code = 202
        response_message = "Aceptado"

    class FakeIndexerService:

        def __init__(self):
            self.calls = []

        def index_url(self, url_id):
            self.calls.append(url_id)
            return FakeResult()

    indexer = FakeIndexerService()

    monkeypatch.setattr(
        "gui.pages.indexnow.UrlService",
        lambda: FakeUrlService()
    )

    monkeypatch.setattr(
        "gui.pages.indexnow.DomainService",
        lambda: FakeDomainService()
    )

    monkeypatch.setattr(
        "gui.pages.indexnow.IndexerService",
        lambda: indexer
    )

    messages = []

    monkeypatch.setattr(
        "gui.pages.indexnow.QMessageBox.information",
        lambda *args: messages.append(args)
    )

    from gui.pages.indexnow import IndexNowPage

    app = get_qapplication()
    page = IndexNowPage()

    assert page.table.rowCount() == 1

    page.table.selectRow(0)
    page.send_selected_url()

    assert indexer.calls == [1]
    assert len(messages) == 1
    assert messages[0][1] == "IndexNow"
    assert "correctamente" in messages[0][2]

    page.close()
    app.processEvents()

def test_indexnow_page_invalid_url_id(monkeypatch):

    class FakeUrlService:

        def get_urls(self):
            return [
                UrlRecord(
                    id=1,
                    domain_id=1,
                    url="https://example.com/prueba",
                    status="PENDIENTE"
                )
            ]

        def get_url(self, url_id):
            raise AssertionError(
                "No se debe consultar el servicio con un ID inválido"
            )

    class FakeDomainService:

        def get_domains(self):
            return [
                Domain(
                    id=1,
                    domain="example.com",
                    api_key="TEST_KEY",
                    enabled=True
                )
            ]

    class FakeIndexerService:
        pass

    monkeypatch.setattr(
        "gui.pages.indexnow.UrlService",
        lambda: FakeUrlService()
    )

    monkeypatch.setattr(
        "gui.pages.indexnow.DomainService",
        lambda: FakeDomainService()
    )

    monkeypatch.setattr(
        "gui.pages.indexnow.IndexerService",
        lambda: FakeIndexerService()
    )

    messages = []

    monkeypatch.setattr(
        "gui.pages.indexnow.QMessageBox.critical",
        lambda *args: messages.append(args)
    )

    from gui.pages.indexnow import IndexNowPage

    app = get_qapplication()
    page = IndexNowPage()

    page.table.item(0, 0).setText("ABC")
    page.table.selectRow(0)
    page.send_selected_url()

    assert len(messages) == 1
    assert messages[0][1] == "Error"
    assert messages[0][2] == (
        "El ID de la URL no es válido."
    )

    page.close()
    app.processEvents()


def test_indexnow_page_url_not_found(monkeypatch):

    class FakeUrlService:

        def get_urls(self):
            return [
                UrlRecord(
                    id=1,
                    domain_id=1,
                    url="https://example.com/prueba",
                    status="PENDIENTE"
                )
            ]

        def get_url(self, url_id):
            return None

    class FakeDomainService:

        def get_domains(self):
            return [
                Domain(
                    id=1,
                    domain="example.com",
                    api_key="TEST_KEY",
                    enabled=True
                )
            ]

    class FakeIndexerService:
        pass

    monkeypatch.setattr(
        "gui.pages.indexnow.UrlService",
        lambda: FakeUrlService()
    )

    monkeypatch.setattr(
        "gui.pages.indexnow.DomainService",
        lambda: FakeDomainService()
    )

    monkeypatch.setattr(
        "gui.pages.indexnow.IndexerService",
        lambda: FakeIndexerService()
    )

    messages = []

    monkeypatch.setattr(
        "gui.pages.indexnow.QMessageBox.critical",
        lambda *args: messages.append(args)
    )

    from gui.pages.indexnow import IndexNowPage

    app = get_qapplication()
    page = IndexNowPage()

    page.table.selectRow(0)
    page.send_selected_url()

    assert len(messages) == 1
    assert messages[0][1] == "Error"
    assert messages[0][2] == (
        "No se ha encontrado la URL."
    )

    page.close()
    app.processEvents()

def test_indexnow_page_manual_send_error(monkeypatch):

    url_record = UrlRecord(
        id=1,
        domain_id=1,
        url="https://example.com/error",
        status="PENDIENTE"
    )

    class FakeUrlService:

        def __init__(self):
            self.get_urls_calls = 0

        def get_urls(self):
            self.get_urls_calls += 1
            return [url_record]

        def get_url(self, url_id):
            return url_record

    class FakeDomainService:

        def get_domains(self):
            return [
                Domain(
                    id=1,
                    domain="example.com",
                    api_key="TEST_KEY",
                    enabled=True
                )
            ]

    class FakeResult:

        status = "ERROR"
        url = "https://example.com/error"
        response_code = 500
        response_message = "Error de prueba"

    class FakeIndexerService:

        def __init__(self):
            self.calls = []

        def index_url(self, url_id):
            self.calls.append(url_id)
            return FakeResult()

    url_service = FakeUrlService()
    indexer = FakeIndexerService()

    monkeypatch.setattr(
        "gui.pages.indexnow.UrlService",
        lambda: url_service
    )

    monkeypatch.setattr(
        "gui.pages.indexnow.DomainService",
        lambda: FakeDomainService()
    )

    monkeypatch.setattr(
        "gui.pages.indexnow.IndexerService",
        lambda: indexer
    )

    messages = []

    monkeypatch.setattr(
        "gui.pages.indexnow.QMessageBox.warning",
        lambda *args: messages.append(args)
    )

    from gui.pages.indexnow import IndexNowPage

    app = get_qapplication()
    page = IndexNowPage()

    assert page.table.rowCount() == 1
    assert url_service.get_urls_calls == 1

    page.table.selectRow(0)
    page.send_selected_url()

    assert indexer.calls == [1]

    assert len(messages) == 1
    assert messages[0][1] == "IndexNow"
    assert "no ha podido aceptar" in messages[0][2]
    assert "https://example.com/error" in messages[0][2]
    assert "500" in messages[0][2]
    assert "Error de prueba" in messages[0][2]

    assert url_service.get_urls_calls == 2

    page.close()
    app.processEvents()

def test_indexnow_page_handles_value_error(monkeypatch):

    url_record = UrlRecord(
        id=1,
        domain_id=1,
        url="https://example.com/prueba",
        status="PENDIENTE"
    )

    class FakeUrlService:

        def get_urls(self):
            return [url_record]

        def get_url(self, url_id):
            return url_record

    class FakeDomainService:

        def get_domains(self):
            return [
                Domain(
                    id=1,
                    domain="example.com",
                    api_key="TEST_KEY",
                    enabled=True
                )
            ]

    class FakeIndexerService:

        def index_url(self, url_id):
            raise ValueError("Error de validación")

    monkeypatch.setattr(
        "gui.pages.indexnow.UrlService",
        lambda: FakeUrlService()
    )

    monkeypatch.setattr(
        "gui.pages.indexnow.DomainService",
        lambda: FakeDomainService()
    )

    monkeypatch.setattr(
        "gui.pages.indexnow.IndexerService",
        lambda: FakeIndexerService()
    )

    messages = []

    monkeypatch.setattr(
        "gui.pages.indexnow.QMessageBox.warning",
        lambda *args: messages.append(args)
    )

    from gui.pages.indexnow import IndexNowPage

    app = get_qapplication()
    page = IndexNowPage()

    page.table.selectRow(0)
    page.send_selected_url()

    assert len(messages) == 1
    assert messages[0][1] == "IndexNow"
    assert messages[0][2] == "Error de validación"

    page.close()
    app.processEvents()


def test_indexnow_page_handles_unexpected_error(monkeypatch):

    url_record = UrlRecord(
        id=1,
        domain_id=1,
        url="https://example.com/prueba",
        status="PENDIENTE"
    )

    class FakeUrlService:

        def get_urls(self):
            return [url_record]

        def get_url(self, url_id):
            return url_record

    class FakeDomainService:

        def get_domains(self):
            return [
                Domain(
                    id=1,
                    domain="example.com",
                    api_key="TEST_KEY",
                    enabled=True
                )
            ]

    class FakeIndexerService:

        def index_url(self, url_id):
            raise RuntimeError("Fallo inesperado")

    monkeypatch.setattr(
        "gui.pages.indexnow.UrlService",
        lambda: FakeUrlService()
    )

    monkeypatch.setattr(
        "gui.pages.indexnow.DomainService",
        lambda: FakeDomainService()
    )

    monkeypatch.setattr(
        "gui.pages.indexnow.IndexerService",
        lambda: FakeIndexerService()
    )

    messages = []

    monkeypatch.setattr(
        "gui.pages.indexnow.QMessageBox.critical",
        lambda *args: messages.append(args)
    )

    from gui.pages.indexnow import IndexNowPage

    app = get_qapplication()
    page = IndexNowPage()

    page.table.selectRow(0)
    page.send_selected_url()

    assert len(messages) == 1
    assert messages[0][1] == "Error"
    assert (
        messages[0][2]
        == (
            "Se ha producido un error al enviar "
            "la URL a IndexNow:\n\nFallo inesperado"
        )
    )

    page.close()
    app.processEvents()
