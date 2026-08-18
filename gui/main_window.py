from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QStackedWidget,
)

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