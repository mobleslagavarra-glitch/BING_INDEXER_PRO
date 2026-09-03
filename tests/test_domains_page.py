from PySide6.QtWidgets import QApplication
from models.domain import Domain



def get_qapplication():

    app = QApplication.instance()

    if app is None:
        app = QApplication([])

    return app


def test_domains_page_creates_ui(monkeypatch):

    class FakeDomainService:

        def get_domains(self):
            return []

    monkeypatch.setattr(
        "gui.pages.domains.DomainService",
        lambda: FakeDomainService()
    )

    from gui.pages.domains import DomainsPage

    app = get_qapplication()
    page = DomainsPage()

    assert page.table.columnCount() == 4
    assert page.table.horizontalHeaderItem(0).text() == "ID"
    assert page.table.horizontalHeaderItem(1).text() == "Dominio"
    assert page.table.horizontalHeaderItem(2).text() == "API Key"
    assert page.table.horizontalHeaderItem(3).text() == "Estado"

    assert page.btn_add.text() == "➕ Añadir"
    assert page.btn_edit.text() == "✏️ Editar"
    assert page.btn_delete.text() == "🗑️ Eliminar"
    assert page.btn_refresh.text() == "🔄 Actualizar"

    page.close()
    app.processEvents()


def test_domains_page_loads_domains(monkeypatch):

    domains = [
        Domain(
            id=1,
            domain="example.com",
            api_key="KEY_ONE",
            enabled=True
        ),
        Domain(
            id=2,
            domain="example.org",
            api_key="KEY_TWO",
            enabled=False
        ),
    ]

    class FakeDomainService:

        def get_domains(self):
            return domains

    monkeypatch.setattr(
        "gui.pages.domains.DomainService",
        lambda: FakeDomainService()
    )

    from gui.pages.domains import DomainsPage

    app = get_qapplication()
    page = DomainsPage()

    assert page.table.rowCount() == 2

    assert page.table.item(0, 0).text() == "1"
    assert page.table.item(0, 1).text() == "example.com"
    assert page.table.item(0, 2).text() == "KEY_ONE"
    assert page.table.item(0, 3).text() == "Activo"

    assert page.table.item(1, 0).text() == "2"
    assert page.table.item(1, 1).text() == "example.org"
    assert page.table.item(1, 2).text() == "KEY_TWO"
    assert page.table.item(1, 3).text() == "Desactivado"

    page.close()
    app.processEvents()


def test_domains_page_refresh_reloads_domains(monkeypatch):

    class FakeDomainService:

        def __init__(self):
            self.calls = 0

        def get_domains(self):

            self.calls += 1

            if self.calls == 1:
                return [
                    Domain(
                        id=1,
                        domain="old.example.com",
                        api_key="OLD",
                        enabled=True
                    )
                ]

            return [
                Domain(
                    id=2,
                    domain="new.example.com",
                    api_key="NEW",
                    enabled=True
                ),
                Domain(
                    id=3,
                    domain="another.example.com",
                    api_key="ANOTHER",
                    enabled=False
                )
            ]

    service = FakeDomainService()

    monkeypatch.setattr(
        "gui.pages.domains.DomainService",
        lambda: service
    )

    from gui.pages.domains import DomainsPage

    app = get_qapplication()
    page = DomainsPage()

    assert service.calls == 1
    assert page.table.rowCount() == 1
    assert page.table.item(0, 1).text() == "old.example.com"

    page.load_domains()

    assert service.calls == 2
    assert page.table.rowCount() == 2
    assert page.table.item(0, 1).text() == "new.example.com"
    assert page.table.item(1, 1).text() == "another.example.com"

    page.close()
    app.processEvents()


def test_domains_page_handles_load_error(monkeypatch):

    class FakeDomainService:

        def get_domains(self):
            raise RuntimeError("Error de prueba")

    monkeypatch.setattr(
        "gui.pages.domains.DomainService",
        lambda: FakeDomainService()
    )

    messages = []

    monkeypatch.setattr(
        "gui.pages.domains.QMessageBox.critical",
        lambda *args: messages.append(args)
    )

    from gui.pages.domains import DomainsPage

    app = get_qapplication()
    page = DomainsPage()

    assert len(messages) == 1
    assert messages[0][1] == "Error"
    assert "No se pudieron cargar los dominios" in messages[0][2]
    assert "Error de prueba" in messages[0][2]

    page.close()
    app.processEvents()


def test_domains_page_edit_without_selection(monkeypatch):

    class FakeDomainService:

        def get_domains(self):
            return []

    monkeypatch.setattr(
        "gui.pages.domains.DomainService",
        lambda: FakeDomainService()
    )

    messages = []

    monkeypatch.setattr(
        "gui.pages.domains.QMessageBox.warning",
        lambda *args: messages.append(args)
    )

    from gui.pages.domains import DomainsPage

    app = get_qapplication()
    page = DomainsPage()

    page.edit_domain()

    assert len(messages) == 1
    assert messages[0][1] == "Editar dominio"
    assert messages[0][2] == (
        "Selecciona un dominio de la lista."
    )

    page.close()
    app.processEvents()


def test_domains_page_delete_without_selection(monkeypatch):

    class FakeDomainService:

        def get_domains(self):
            return []

    monkeypatch.setattr(
        "gui.pages.domains.DomainService",
        lambda: FakeDomainService()
    )

    messages = []

    monkeypatch.setattr(
        "gui.pages.domains.QMessageBox.warning",
        lambda *args: messages.append(args)
    )

    from gui.pages.domains import DomainsPage

    app = get_qapplication()
    page = DomainsPage()

    page.delete_domain()

    assert len(messages) == 1
    assert messages[0][1] == "Eliminar dominio"
    assert messages[0][2] == (
        "Selecciona un dominio de la lista."
    )

    page.close()
    app.processEvents()

