from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QStackedWidget,
)

from PySide6.QtCore import QTimer

from core.version import Version

from gui.menu_bar import MainMenu
from gui.status_bar import StatusBar
from gui.navigation import Navigation

from gui.pages.dashboard import DashboardPage
from gui.pages.domains import DomainsPage
from gui.pages.urls import UrlsPage
from gui.pages.indexnow import IndexNowPage
from gui.pages.history import HistoryPage
from gui.pages.settings import SettingsPage

from services.automation_service import AutomationService
from services.settings_service import SettingsService


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle(
            f"{Version.APP_NAME} {Version.VERSION}"
        )

        self.resize(1280, 720)

        self.navigation = Navigation()

        MainMenu(self)

        self.setStatusBar(StatusBar())

        self.stack = QStackedWidget()

        self.stack.addWidget(DashboardPage())
        self.stack.addWidget(DomainsPage())
        self.stack.addWidget(UrlsPage())
        self.stack.addWidget(IndexNowPage())
        self.stack.addWidget(HistoryPage())

        self.settings_page = SettingsPage()

        self.stack.addWidget(
            self.settings_page
        )

        self.settings_page.settings_saved.connect(
            self.update_automation_interval
        )

        self.navigation.currentRowChanged.connect(
            self.stack.setCurrentIndex
        )

        central = QWidget()

        layout = QHBoxLayout()

        layout.addWidget(self.navigation)
        layout.addWidget(self.stack)

        central.setLayout(layout)

        self.setCentralWidget(central)

        # Automatización de IndexNow
        self.automation_service = AutomationService()
        self.settings_service = SettingsService()

        self.automation_timer = QTimer(self)

        self.automation_timer.timeout.connect(
            self.run_automation
        )

        self.update_automation_interval()

    def update_automation_interval(self):

        try:

            interval = self.settings_service.get(
                "indexnow_interval",
                "1"
            )

            interval_minutes = int(interval)

            if interval_minutes < 1:
                interval_minutes = 1

            interval_ms = interval_minutes * 60 * 1000

            self.automation_timer.setInterval(
                interval_ms
            )

            if self.automation_service.is_enabled():

                if not self.automation_timer.isActive():
                    self.automation_timer.start()

                print(
                    f"Automatización ACTIVADA - "
                    f"intervalo: {interval_minutes} minuto(s)"
                )

            else:

                if self.automation_timer.isActive():
                    self.automation_timer.stop()

                print(
                    "Automatización DESACTIVADA"
                )

        except Exception as error:

            self.automation_timer.setInterval(
                self.automation_service.INTERVAL_MS
            )

            print(
                f"Error leyendo intervalo de automatización: {error}"
            )

    def run_automation(self):

        try:

            self.automation_service.run()

        except Exception as error:

            print(
                f"Error en automatización de IndexNow: {error}"
            )
