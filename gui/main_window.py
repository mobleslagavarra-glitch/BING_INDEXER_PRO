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


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle(
            f"{Version.APP_NAME} {Version.VERSION}"
        )

        self.resize(1280, 720)

        # Navegación lateral
        self.navigation = Navigation()

        # Menú superior
        MainMenu(self)

        # Barra de estado
        self.setStatusBar(StatusBar())

        # Páginas
        self.stack = QStackedWidget()

        self.stack.addWidget(DashboardPage())
        self.stack.addWidget(DomainsPage())
        self.stack.addWidget(UrlsPage())
        self.stack.addWidget(IndexNowPage())
        self.stack.addWidget(HistoryPage())
        self.stack.addWidget(SettingsPage())

        # Conectar navegación lateral con las páginas
        self.navigation.currentRowChanged.connect(
            self.stack.setCurrentIndex
        )

        # Contenedor principal
        central = QWidget()

        layout = QHBoxLayout()

        layout.addWidget(self.navigation)
        layout.addWidget(self.stack)

        central.setLayout(layout)

        self.setCentralWidget(central)

        # Automatización de IndexNow
        self.automation_service = AutomationService()

        self.automation_timer = QTimer(self)

        self.automation_timer.setInterval(
            self.automation_service.INTERVAL_MS
        )

        self.automation_timer.timeout.connect(
            self.run_automation
        )

        self.automation_timer.start()

    def run_automation(self):

        try:

            self.automation_service.run()

        except Exception as error:

            print(
                f"Error en automatización de IndexNow: {error}"
            )
