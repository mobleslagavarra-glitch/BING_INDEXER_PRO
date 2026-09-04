from PySide6.QtCore import QTimer, Signal
from PySide6.QtWidgets import QApplication, QWidget

from gui.main_window import MainWindow


def get_qapplication():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


class FakeTimer:

    def __init__(self, *args, **kwargs):
        self.interval = None
        self.active = False
        self.timeout = self
        self.callback = None

    def connect(self, callback):
        self.callback = callback

    def setInterval(self, value):
        self.interval = value

    def isActive(self):
        return self.active

    def start(self):
        self.active = True

    def stop(self):
        self.active = False

    @staticmethod
    def singleShot(ms, callback):
        pass


class FakeSettingsService:

    def __init__(self, interval="1"):
        self.interval = interval

    def get(self, key, default=None):
        if key == "indexnow_interval":
            return self.interval
        return default


class FakeAutomationService:

    INTERVAL_MS = 60000

    def __init__(self, enabled=True):
        self.enabled = enabled
        self.last_run = None
        self.processed_count = 0
        self.success_count = 0
        self.error_count = 0
        self.run_calls = 0

    def is_enabled(self):
        return self.enabled

    def run(self):
        self.run_calls += 1


class FakePage(QWidget):

    def __init__(self):
        super().__init__()
        self.update_calls = []
        self.load_statistics_calls = 0

    def update_automation_status(self, *args):
        self.update_calls.append(args)

    def load_statistics(self):
        self.load_statistics_calls += 1


class FakeSettingsPage(FakePage):

    settings_saved = Signal()


def create_window(
    monkeypatch,
    interval="1",
    enabled=True
):

    get_qapplication()

    settings = FakeSettingsService(interval)
    automation = FakeAutomationService(enabled)

    monkeypatch.setattr(
        "gui.main_window.SettingsService",
        lambda: settings
    )

    monkeypatch.setattr(
        "gui.main_window.AutomationService",
        lambda: automation
    )

    monkeypatch.setattr(
        "gui.main_window.QTimer",
        FakeTimer
    )

    monkeypatch.setattr(
        "gui.main_window.DashboardPage",
        FakePage
    )

    monkeypatch.setattr(
        "gui.main_window.DomainsPage",
        FakePage
    )

    monkeypatch.setattr(
        "gui.main_window.UrlsPage",
        FakePage
    )

    monkeypatch.setattr(
        "gui.main_window.IndexNowPage",
        FakePage
    )

    monkeypatch.setattr(
        "gui.main_window.HistoryPage",
        FakePage
    )

    monkeypatch.setattr(
        "gui.main_window.SettingsPage",
        FakeSettingsPage
    )

    window = MainWindow()

    return window, settings, automation


def test_main_window_title_and_size(monkeypatch):

    window, settings, automation = create_window(
        monkeypatch
    )

    assert window.windowTitle() == "BING INDEXER PRO 0.1.0"
    assert window.width() == 1280
    assert window.height() == 720


def test_main_window_creates_six_pages(monkeypatch):

    window, settings, automation = create_window(
        monkeypatch
    )

    assert window.stack.count() == 6
    assert window.dashboard_page is not None
    assert window.settings_page is not None


def test_main_window_initial_page_is_dashboard(monkeypatch):

    window, settings, automation = create_window(
        monkeypatch
    )

    assert window.stack.currentIndex() == 0
    assert window.navigation.currentRow() == -1


def test_main_window_navigation_changes_stack(monkeypatch):

    window, settings, automation = create_window(
        monkeypatch
    )

    window.navigation.setCurrentRow(3)

    assert window.stack.currentIndex() == 3

    window.navigation.setCurrentRow(5)

    assert window.stack.currentIndex() == 5


def test_main_window_automation_interval(monkeypatch):

    window, settings, automation = create_window(
        monkeypatch,
        interval="5",
        enabled=True
    )

    assert window.automation_timer.interval == 300000
    assert window.automation_timer.isActive() is True


def test_main_window_automation_disabled(monkeypatch):

    window, settings, automation = create_window(
        monkeypatch,
        interval="5",
        enabled=False
    )

    assert window.automation_timer.interval == 300000
    assert window.automation_timer.isActive() is False


def test_main_window_update_interval_clamps_zero(
    monkeypatch
):

    window, settings, automation = create_window(
        monkeypatch,
        interval="0",
        enabled=False
    )

    window.update_automation_interval()

    assert window.automation_timer.interval == 60000


def test_main_window_update_automation_display(
    monkeypatch
):

    window, settings, automation = create_window(
        monkeypatch
    )

    window.update_automation_display(
        True,
        5
    )

    assert len(window.dashboard_page.update_calls) >= 1

    call = window.dashboard_page.update_calls[-1]

    assert call[0] is True
    assert call[1] == 5
    assert call[3] == 0
    assert call[4] == 0
    assert call[5] == 0


def test_main_window_run_automation(monkeypatch):

    window, settings, automation = create_window(
        monkeypatch,
        interval="2",
        enabled=True
    )

    window.run_automation()

    assert automation.run_calls == 1
    assert window.dashboard_page.load_statistics_calls == 1
    assert len(window.dashboard_page.update_calls) >= 2


def test_main_window_invalid_interval_uses_default(
    monkeypatch
):

    window, settings, automation = create_window(
        monkeypatch,
        interval="invalido",
        enabled=True
    )

    assert window.automation_timer.interval == automation.INTERVAL_MS
