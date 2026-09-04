from PySide6.QtWidgets import QApplication, QMessageBox

from gui.pages.history import HistoryPage


def get_qapplication():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


class FakeHistoryService:

    def __init__(self, entries=None):
        self.entries = entries or []
        self.clear_calls = 0

    def get_all(self):
        return list(self.entries)

    def clear(self):
        self.clear_calls += 1
        deleted = len(self.entries)
        self.entries.clear()
        return deleted


def create_page(monkeypatch, entries=None):
    get_qapplication()

    service = FakeHistoryService(entries)

    monkeypatch.setattr(
        "gui.pages.history.HistoryService",
        lambda: service
    )

    page = HistoryPage()

    return page, service


def test_history_page_initial_structure(monkeypatch):

    page, service = create_page(monkeypatch)

    assert page.table.columnCount() == 7
    assert page.table.rowCount() == 0

    headers = [
        page.table.horizontalHeaderItem(column).text()
        for column in range(7)
    ]

    assert headers == [
        "ID",
        "Fecha / Hora",
        "Tipo",
        "Descripción",
        "Procesadas",
        "Correctas",
        "Errores",
    ]

    assert page.btn_clear.text() == "Limpiar historial"
    assert page.btn_refresh.text() == "Actualizar"


def test_history_page_load_history(monkeypatch):

    entries = [
        (
            1,
            "2026-08-26 21:00:00",
            "INDEXACION_COMPLETADA",
            "URL enviada correctamente",
            1,
            1,
            0,
        ),
        (
            2,
            "2026-08-26 21:01:00",
            "AUTOMATIZACION_EJECUTADA",
            "Ejecución automática de IndexNow",
            5,
            4,
            1,
        ),
    ]

    page, service = create_page(
        monkeypatch,
        entries
    )

    assert page.table.rowCount() == 2

    assert page.table.item(0, 0).text() == "1"
    assert page.table.item(0, 1).text() == "2026-08-26 21:00:00"
    assert page.table.item(0, 2).text() == "INDEXACION_COMPLETADA"
    assert page.table.item(0, 3).text() == "URL enviada correctamente"
    assert page.table.item(0, 4).text() == "1"
    assert page.table.item(0, 5).text() == "1"
    assert page.table.item(0, 6).text() == "0"

    assert page.table.item(1, 2).text() == "AUTOMATIZACION_EJECUTADA"
    assert page.table.item(1, 4).text() == "5"
    assert page.table.item(1, 5).text() == "4"
    assert page.table.item(1, 6).text() == "1"


def test_history_page_load_history_error(monkeypatch):

    get_qapplication()

    class ErrorService:

        def get_all(self):
            raise RuntimeError("Error de prueba")

    monkeypatch.setattr(
        "gui.pages.history.HistoryService",
        ErrorService
    )

    messages = []

    def fake_critical(*args, **kwargs):
        messages.append(args)

    monkeypatch.setattr(
        QMessageBox,
        "critical",
        fake_critical
    )

    page = HistoryPage()

    assert page.table.rowCount() == 0
    assert len(messages) == 1
    assert messages[0][1] == "Error"
    assert "Error de prueba" in messages[0][2]


def test_history_page_refresh(monkeypatch):

    entries = [
        (
            1,
            "2026-08-26 21:00:00",
            "TEST",
            "Primero",
            1,
            1,
            0,
        )
    ]

    page, service = create_page(
        monkeypatch,
        entries
    )

    assert page.table.rowCount() == 1

    service.entries.append(
        (
            2,
            "2026-08-26 21:01:00",
            "TEST",
            "Segundo",
            2,
            2,
            0,
        )
    )

    page.load_history()

    assert page.table.rowCount() == 2
    assert page.table.item(1, 3).text() == "Segundo"


def test_history_page_clear_empty(monkeypatch):

    page, service = create_page(monkeypatch)

    messages = []

    def fake_information(*args, **kwargs):
        messages.append(args)

    monkeypatch.setattr(
        QMessageBox,
        "information",
        fake_information
    )

    page.clear_history()

    assert service.clear_calls == 0
    assert len(messages) == 1
    assert messages[0][1] == "Historial"
    assert messages[0][2] == "El historial ya está vacío."


def test_history_page_clear_cancelled(monkeypatch):

    entries = [
        (
            1,
            "2026-08-26 21:00:00",
            "TEST",
            "Evento",
            1,
            1,
            0,
        )
    ]

    page, service = create_page(
        monkeypatch,
        entries
    )

    monkeypatch.setattr(
        QMessageBox,
        "question",
        lambda *args, **kwargs:
            QMessageBox.StandardButton.No
    )

    page.clear_history()

    assert service.clear_calls == 0
    assert page.table.rowCount() == 1


def test_history_page_clear_success(monkeypatch):

    entries = [
        (
            1,
            "2026-08-26 21:00:00",
            "TEST",
            "Evento",
            1,
            1,
            0,
        ),
        (
            2,
            "2026-08-26 21:01:00",
            "TEST",
            "Evento 2",
            2,
            2,
            0,
        ),
    ]

    page, service = create_page(
        monkeypatch,
        entries
    )

    monkeypatch.setattr(
        QMessageBox,
        "question",
        lambda *args, **kwargs:
            QMessageBox.StandardButton.Yes
    )

    messages = []

    monkeypatch.setattr(
        QMessageBox,
        "information",
        lambda *args, **kwargs:
            messages.append(args)
    )

    page.clear_history()

    assert service.clear_calls == 1
    assert page.table.rowCount() == 0
    assert len(messages) == 1
    assert messages[0][1] == "Historial"
    assert "Se han eliminado 2 registro(s)" in messages[0][2]
