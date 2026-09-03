from PySide6.QtWidgets import QApplication, QDialog

from models.url import UrlRecord
from models.domain import Domain


def get_qapplication():

    app = QApplication.instance()

    if app is None:
        app = QApplication([])

    return app


def test_urls_page_creates_ui(monkeypatch):

    class FakeUrlService:

        def get_urls(self):
            return []

    class FakeDomainService:

        def get_domains(self):
            return []

    monkeypatch.setattr(
        "gui.pages.urls.UrlService",
        lambda: FakeUrlService()
    )

    monkeypatch.setattr(
        "gui.pages.urls.DomainService",
        lambda: FakeDomainService()
    )

    from gui.pages.urls import UrlsPage

    app = get_qapplication()
    page = UrlsPage()

    assert page.table.columnCount() == 6

    assert page.table.horizontalHeaderItem(0).text() == "ID"
    assert page.table.horizontalHeaderItem(1).text() == "Dominio"
    assert page.table.horizontalHeaderItem(2).text() == "URL"
    assert page.table.horizontalHeaderItem(3).text() == "Estado"
    assert page.table.horizontalHeaderItem(4).text() == "Código"
    assert page.table.horizontalHeaderItem(5).text() == "Mensaje"

    assert page.btn_add.text() == "➕ Añadir"
    assert page.btn_edit.text() == "✏️ Editar"
    assert page.btn_delete.text() == "🗑️ Eliminar"
    assert page.btn_import.text() == "📥 Importar Excel"
    assert page.btn_send.text() == "🚀 Enviar pendientes"
    assert page.btn_refresh.text() == "🔄 Actualizar"

    page.close()
    app.processEvents()


def test_urls_page_loads_urls(monkeypatch):

    urls = [
        UrlRecord(
            id=1,
            domain_id=10,
            url="https://example.com/uno",
            status="PENDIENTE",
            response_code=None,
            response_message=""
        ),
        UrlRecord(
            id=2,
            domain_id=20,
            url="https://example.org/dos",
            status="ENVIADA",
            response_code=200,
            response_message="OK"
        ),
        UrlRecord(
            id=3,
            domain_id=10,
            url="https://example.com/tres",
            status="ERROR",
            response_code=500,
            response_message="Error servidor"
        ),
    ]

    domains = [
        Domain(
            id=10,
            domain="example.com",
            api_key="KEY_ONE",
            enabled=True
        ),
        Domain(
            id=20,
            domain="example.org",
            api_key="KEY_TWO",
            enabled=True
        ),
    ]

    class FakeUrlService:

        def get_urls(self):
            return urls

    class FakeDomainService:

        def get_domains(self):
            return domains

    monkeypatch.setattr(
        "gui.pages.urls.UrlService",
        lambda: FakeUrlService()
    )

    monkeypatch.setattr(
        "gui.pages.urls.DomainService",
        lambda: FakeDomainService()
    )

    from gui.pages.urls import UrlsPage

    app = get_qapplication()
    page = UrlsPage()

    assert page.table.rowCount() == 3

    assert page.table.item(0, 0).text() == "1"
    assert page.table.item(0, 1).text() == "example.com"
    assert page.table.item(0, 2).text() == "https://example.com/uno"
    assert page.table.item(0, 3).text() == "PENDIENTE"
    assert page.table.item(0, 4).text() == ""
    assert page.table.item(0, 5).text() == ""

    assert page.table.item(1, 0).text() == "2"
    assert page.table.item(1, 1).text() == "example.org"
    assert page.table.item(1, 2).text() == "https://example.org/dos"
    assert page.table.item(1, 3).text() == "ENVIADA"
    assert page.table.item(1, 4).text() == "200"
    assert page.table.item(1, 5).text() == "OK"

    assert page.table.item(2, 0).text() == "3"
    assert page.table.item(2, 1).text() == "example.com"
    assert page.table.item(2, 2).text() == "https://example.com/tres"
    assert page.table.item(2, 3).text() == "ERROR"
    assert page.table.item(2, 4).text() == "500"
    assert page.table.item(2, 5).text() == "Error servidor"

    page.close()
    app.processEvents()


def test_urls_page_refresh_reloads_urls(monkeypatch):

    class FakeUrlService:

        def __init__(self):
            self.calls = 0

        def get_urls(self):

            self.calls += 1

            if self.calls == 1:
                return [
                    UrlRecord(
                        id=1,
                        domain_id=10,
                        url="https://example.com/old",
                        status="PENDIENTE",
                        response_code=None,
                        response_message=""
                    )
                ]

            return [
                UrlRecord(
                    id=2,
                    domain_id=10,
                    url="https://example.com/new",
                    status="ENVIADA",
                    response_code=200,
                    response_message="OK"
                ),
                UrlRecord(
                    id=3,
                    domain_id=20,
                    url="https://example.org/other",
                    status="PENDIENTE",
                    response_code=None,
                    response_message=""
                ),
            ]

    class FakeDomainService:

        def get_domains(self):
            return [
                Domain(
                    id=10,
                    domain="example.com",
                    api_key="KEY_ONE",
                    enabled=True
                ),
                Domain(
                    id=20,
                    domain="example.org",
                    api_key="KEY_TWO",
                    enabled=True
                ),
            ]

    url_service = FakeUrlService()

    monkeypatch.setattr(
        "gui.pages.urls.UrlService",
        lambda: url_service
    )

    monkeypatch.setattr(
        "gui.pages.urls.DomainService",
        lambda: FakeDomainService()
    )

    from gui.pages.urls import UrlsPage

    app = get_qapplication()
    page = UrlsPage()

    assert url_service.calls == 1
    assert page.table.rowCount() == 1
    assert page.table.item(0, 2).text() == (
        "https://example.com/old"
    )

    page.load_urls()

    assert url_service.calls == 2
    assert page.table.rowCount() == 2
    assert page.table.item(0, 2).text() == (
        "https://example.com/new"
    )
    assert page.table.item(1, 2).text() == (
        "https://example.org/other"
    )

    page.close()
    app.processEvents()


def test_urls_page_handles_load_error(monkeypatch):

    class FakeUrlService:

        def get_urls(self):
            raise RuntimeError("Error de prueba")

    class FakeDomainService:

        def get_domains(self):
            return []

    monkeypatch.setattr(
        "gui.pages.urls.UrlService",
        lambda: FakeUrlService()
    )

    monkeypatch.setattr(
        "gui.pages.urls.DomainService",
        lambda: FakeDomainService()
    )

    messages = []

    monkeypatch.setattr(
        "gui.pages.urls.QMessageBox.critical",
        lambda *args: messages.append(args)
    )

    from gui.pages.urls import UrlsPage

    app = get_qapplication()
    page = UrlsPage()

    assert len(messages) == 1
    assert messages[0][1] == "Error"
    assert "No se pudieron cargar las URLs" in messages[0][2]
    assert "Error de prueba" in messages[0][2]

    page.close()
    app.processEvents()


def test_urls_page_edit_without_selection(monkeypatch):

    class FakeUrlService:

        def get_urls(self):
            return []

    class FakeDomainService:

        def get_domains(self):
            return []

    monkeypatch.setattr(
        "gui.pages.urls.UrlService",
        lambda: FakeUrlService()
    )

    monkeypatch.setattr(
        "gui.pages.urls.DomainService",
        lambda: FakeDomainService()
    )

    messages = []

    monkeypatch.setattr(
        "gui.pages.urls.QMessageBox.information",
        lambda *args: messages.append(args)
    )

    from gui.pages.urls import UrlsPage

    app = get_qapplication()
    page = UrlsPage()

    page.edit_url()

    assert len(messages) == 1
    assert messages[0][1] == "Editar URL"
    assert messages[0][2] == "Selecciona una URL."

    page.close()
    app.processEvents()


def test_urls_page_delete_without_selection(monkeypatch):

    class FakeUrlService:

        def get_urls(self):
            return []

    class FakeDomainService:

        def get_domains(self):
            return []

    monkeypatch.setattr(
        "gui.pages.urls.UrlService",
        lambda: FakeUrlService()
    )

    monkeypatch.setattr(
        "gui.pages.urls.DomainService",
        lambda: FakeDomainService()
    )

    messages = []

    monkeypatch.setattr(
        "gui.pages.urls.QMessageBox.information",
        lambda *args: messages.append(args)
    )

    from gui.pages.urls import UrlsPage

    app = get_qapplication()
    page = UrlsPage()

    page.delete_url()

    assert len(messages) == 1
    assert messages[0][1] == "Eliminar URL"
    assert messages[0][2] == "Selecciona una URL."

    page.close()
    app.processEvents()
def test_urls_page_add_without_domains(monkeypatch):

    class FakeUrlService:

        def get_urls(self):
            return []

    class FakeDomainService:

        def get_domains(self):
            return []

    monkeypatch.setattr(
        "gui.pages.urls.UrlService",
        lambda: FakeUrlService()
    )

    monkeypatch.setattr(
        "gui.pages.urls.DomainService",
        lambda: FakeDomainService()
    )

    messages = []

    monkeypatch.setattr(
        "gui.pages.urls.QMessageBox.warning",
        lambda *args: messages.append(args)
    )

    from gui.pages.urls import UrlsPage

    app = get_qapplication()
    page = UrlsPage()

    page.add_url()

    assert len(messages) == 1
    assert messages[0][1] == "Sin dominios"
    assert messages[0][2] == (
        "Debes crear al menos un dominio antes de añadir una URL."
    )

    page.close()
    app.processEvents()


def test_urls_page_add_url_success(monkeypatch):

    domains = [
        Domain(
            id=10,
            domain="example.com",
            api_key="KEY_ONE",
            enabled=True
        )
    ]

    class FakeUrlService:

        def __init__(self):
            self.added = None

        def get_urls(self):
            return []

        def add_url(self, domain_id, url):
            self.added = (domain_id, url)

    class FakeDomainService:

        def get_domains(self):
            return domains

    class FakeUrlDialog:

        def __init__(self, domains, parent=None):
            self.domains = domains
            self.parent = parent

        def exec(self):
            return QDialog.DialogCode.Accepted

        def get_data(self):
            return {
                "domain_id": 10,
                "url": "https://example.com/nueva"
            }

    url_service = FakeUrlService()

    monkeypatch.setattr(
        "gui.pages.urls.UrlService",
        lambda: url_service
    )

    monkeypatch.setattr(
        "gui.pages.urls.DomainService",
        lambda: FakeDomainService()
    )

    monkeypatch.setattr(
        "gui.pages.urls.UrlDialog",
        FakeUrlDialog
    )

    from gui.pages.urls import UrlsPage

    app = get_qapplication()
    page = UrlsPage()

    page.add_url()

    assert url_service.added == (
        10,
        "https://example.com/nueva"
    )

    page.close()
    app.processEvents()


def test_urls_page_add_url_cancelled(monkeypatch):

    domains = [
        Domain(
            id=10,
            domain="example.com",
            api_key="KEY_ONE",
            enabled=True
        )
    ]

    class FakeUrlService:

        def __init__(self):
            self.added = False

        def get_urls(self):
            return []

        def add_url(self, domain_id, url):
            self.added = True

    class FakeDomainService:

        def get_domains(self):
            return domains

    class FakeUrlDialog:

        def __init__(self, domains, parent=None):
            pass

        def exec(self):
            return QDialog.DialogCode.Rejected

    url_service = FakeUrlService()

    monkeypatch.setattr(
        "gui.pages.urls.UrlService",
        lambda: url_service
    )

    monkeypatch.setattr(
        "gui.pages.urls.DomainService",
        lambda: FakeDomainService()
    )

    monkeypatch.setattr(
        "gui.pages.urls.UrlDialog",
        FakeUrlDialog
    )

    from gui.pages.urls import UrlsPage

    app = get_qapplication()
    page = UrlsPage()

    page.add_url()

    assert url_service.added is False

    page.close()
    app.processEvents()


def test_urls_page_add_url_error(monkeypatch):

    domains = [
        Domain(
            id=10,
            domain="example.com",
            api_key="KEY_ONE",
            enabled=True
        )
    ]

    class FakeUrlService:

        def get_urls(self):
            return []

        def add_url(self, domain_id, url):
            raise ValueError("URL duplicada")

    class FakeDomainService:

        def get_domains(self):
            return domains

    class FakeUrlDialog:

        def __init__(self, domains, parent=None):
            pass

        def exec(self):
            return QDialog.DialogCode.Accepted

        def get_data(self):
            return {
                "domain_id": 10,
                "url": "https://example.com/duplicada"
            }

    messages = []

    monkeypatch.setattr(
        "gui.pages.urls.UrlService",
        lambda: FakeUrlService()
    )

    monkeypatch.setattr(
        "gui.pages.urls.DomainService",
        lambda: FakeDomainService()
    )

    monkeypatch.setattr(
        "gui.pages.urls.UrlDialog",
        FakeUrlDialog
    )

    monkeypatch.setattr(
        "gui.pages.urls.QMessageBox.warning",
        lambda *args: messages.append(args)
    )

    from gui.pages.urls import UrlsPage

    app = get_qapplication()
    page = UrlsPage()

    page.add_url()

    assert len(messages) == 1
    assert messages[0][1] == "No se pudo añadir"
    assert messages[0][2] == "URL duplicada"

    page.close()
    app.processEvents()
