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

        self.status_bar = StatusBar()
        self.setStatusBar(self.status_bar)

        self.stack = QStackedWidget()

        self.dashboard_page = DashboardPage()
        self.stack.addWidget(self.dashboard_page)

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

                was_active = self.automation_timer.isActive()

                if not was_active:
                    self.automation_timer.start()

                    QTimer.singleShot(
                        0,
                        self.run_automation
                    )

                self.update_automation_display(
                    True,
                    interval_minutes
                )

                print(
                    f"Automatización ACTIVADA - "
                    f"intervalo: {interval_minutes} minuto(s)"
                )

            else:

                if self.automation_timer.isActive():
                    self.automation_timer.stop()

                self.update_automation_display(
                    False,
                    interval_minutes
                )

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

    def update_automation_display(
        self,
        enabled,
        interval_minutes
    ):

        self.status_bar.update_automation_status(
            enabled,
            interval_minutes,
            self.automation_service.last_run,
            self.automation_service.processed_count,
            self.automation_service.success_count,
            self.automation_service.error_count
        )

        self.dashboard_page.update_automation_status(
            enabled,
            interval_minutes,
            self.automation_service.last_run,
            self.automation_service.processed_count,
            self.automation_service.success_count,
            self.automation_service.error_count
        )

    def run_automation(self):

        try:

            self.automation_service.run()

            interval = self.settings_service.get(
                "indexnow_interval",
                "1"
            )

            self.update_automation_display(
                self.automation_service.is_enabled(),
                int(interval)
            )

            self.dashboard_page.load_statistics()

        except Exception as error:

            print(
                f"Error en automatización de IndexNow: {error}"
            )
