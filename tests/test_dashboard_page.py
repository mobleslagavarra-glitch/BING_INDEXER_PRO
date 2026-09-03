
from datetime import datetime

from PySide6.QtWidgets import QApplication


def get_qapplication():

    app = QApplication.instance()

    if app is None:
        app = QApplication([])

    return app


def test_dashboard_page_creates_ui(monkeypatch):

    class FakeDashboardService:

        def get_statistics(self):
            return {
                "total_domains": 0,
                "active_domains": 0,
                "total_urls": 0,
                "pending_urls": 0,
                "successful_urls": 0,
                "error_urls": 0,
            }

    monkeypatch.setattr(
        "gui.pages.dashboard.DashboardService",
        lambda: FakeDashboardService()
    )

    from gui.pages.dashboard import DashboardPage

    app = get_qapplication()
    page = DashboardPage()

    assert page.lbl_domains.text() == "0"
    assert page.lbl_active.text() == "0"
    assert page.lbl_urls.text() == "0"
    assert page.lbl_pending.text() == "0"
    assert page.lbl_success.text() == "0"
    assert page.lbl_errors.text() == "0"

    assert page.btn_refresh.text() == "🔄 Actualizar"

    page.close()
    app.processEvents()


def test_dashboard_page_loads_statistics(monkeypatch):

    class FakeDashboardService:

        def get_statistics(self):
            return {
                "total_domains": 7,
                "active_domains": 5,
                "total_urls": 20,
                "pending_urls": 4,
                "successful_urls": 14,
                "error_urls": 2,
            }

    monkeypatch.setattr(
        "gui.pages.dashboard.DashboardService",
        lambda: FakeDashboardService()
    )

    from gui.pages.dashboard import DashboardPage

    app = get_qapplication()
    page = DashboardPage()

    assert page.lbl_domains.text() == "7"
    assert page.lbl_active.text() == "5"
    assert page.lbl_urls.text() == "20"
    assert page.lbl_pending.text() == "4"
    assert page.lbl_success.text() == "14"
    assert page.lbl_errors.text() == "2"

    page.close()
    app.processEvents()


def test_dashboard_page_refresh_updates_statistics(monkeypatch):

    class FakeDashboardService:

        def __init__(self):
            self.calls = 0

        def get_statistics(self):
            self.calls += 1

            if self.calls == 1:
                return {
                    "total_domains": 1,
                    "active_domains": 1,
                    "total_urls": 2,
                    "pending_urls": 1,
                    "successful_urls": 1,
                    "error_urls": 0,
                }

            return {
                "total_domains": 10,
                "active_domains": 8,
                "total_urls": 30,
                "pending_urls": 5,
                "successful_urls": 22,
                "error_urls": 3,
            }

    service = FakeDashboardService()

    monkeypatch.setattr(
        "gui.pages.dashboard.DashboardService",
        lambda: service
    )

    from gui.pages.dashboard import DashboardPage

    app = get_qapplication()
    page = DashboardPage()

    assert page.lbl_domains.text() == "1"
    assert page.lbl_urls.text() == "2"

    page.load_statistics()

    assert service.calls == 2
    assert page.lbl_domains.text() == "10"
    assert page.lbl_active.text() == "8"
    assert page.lbl_urls.text() == "30"
    assert page.lbl_pending.text() == "5"
    assert page.lbl_success.text() == "22"
    assert page.lbl_errors.text() == "3"

    page.close()
    app.processEvents()


def test_dashboard_page_update_automation_status_active(monkeypatch):

    class FakeDashboardService:

        def get_statistics(self):
            return {
                "total_domains": 0,
                "active_domains": 0,
                "total_urls": 0,
                "pending_urls": 0,
                "successful_urls": 0,
                "error_urls": 0,
            }

    monkeypatch.setattr(
        "gui.pages.dashboard.DashboardService",
        lambda: FakeDashboardService()
    )

    from gui.pages.dashboard import DashboardPage

    app = get_qapplication()
    page = DashboardPage()

    last_run = datetime(2026, 8, 30, 14, 25, 36)

    page.update_automation_status(
        enabled=True,
        interval_minutes=1,
        last_run=last_run,
        processed=12,
        success=10,
        errors=2
    )

    assert page.lbl_automation_status.text() == (
        "Estado: ACTIVA"
    )

    assert page.lbl_automation_interval.text() == (
        "Intervalo: 1 minuto(s)"
    )

    assert page.lbl_automation_last_run.text() == (
        "Última ejecución: 14:25:36"
    )

    assert page.lbl_automation_processed.text() == (
        "Procesadas: 12"
    )

    assert page.lbl_automation_success.text() == (
        "Correctas: 10"
    )

    assert page.lbl_automation_errors.text() == (
        "Errores: 2"
    )

    page.close()
    app.processEvents()


def test_dashboard_page_update_automation_status_disabled(monkeypatch):

    class FakeDashboardService:

        def get_statistics(self):
            return {
                "total_domains": 0,
                "active_domains": 0,
                "total_urls": 0,
                "pending_urls": 0,
                "successful_urls": 0,
                "error_urls": 0,
            }

    monkeypatch.setattr(
        "gui.pages.dashboard.DashboardService",
        lambda: FakeDashboardService()
    )

    from gui.pages.dashboard import DashboardPage

    app = get_qapplication()
    page = DashboardPage()

    page.update_automation_status(
        enabled=False,
        interval_minutes=1
    )

    assert page.lbl_automation_status.text() == (
        "Estado: DESACTIVADA"
    )

    assert page.lbl_automation_interval.text() == (
        "Intervalo: 1 minuto(s)"
    )

    assert page.lbl_automation_last_run.text() == (
        "Última ejecución: pendiente"
    )

    assert page.lbl_automation_processed.text() == (
        "Procesadas: 0"
    )

    assert page.lbl_automation_success.text() == (
        "Correctas: 0"
    )

    assert page.lbl_automation_errors.text() == (
        "Errores: 0"
    )

    page.close()
    app.processEvents()


def test_dashboard_page_handles_service_error(monkeypatch):

    class FakeDashboardService:

        def get_statistics(self):
            raise RuntimeError("Error de prueba")

    monkeypatch.setattr(
        "gui.pages.dashboard.DashboardService",
        lambda: FakeDashboardService()
    )

    messages = []

    monkeypatch.setattr(
        "builtins.print",
        lambda *args: messages.append(args)
    )

    from gui.pages.dashboard import DashboardPage

    app = get_qapplication()
    page = DashboardPage()

    assert len(messages) == 1
    assert "Error cargando estadísticas" in messages[0][0]
    assert "Error de prueba" in messages[0][0]

    page.close()
    app.processEvents()
