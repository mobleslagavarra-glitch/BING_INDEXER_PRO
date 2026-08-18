from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMessageBox

from core.version import Version


class MainMenu:

    def __init__(self, window):

        self.window = window

        menu = window.menuBar()

        # =========================
        # ARCHIVO
        # =========================

        archivo = menu.addMenu("Archivo")

        salir = QAction("Salir", window)
        salir.triggered.connect(window.close)

        archivo.addAction(salir)

        # =========================
        # DOMINIOS
        # =========================

        dominios = menu.addMenu("Dominios")

        gestionar_dominios = QAction(
            "Gestionar dominios",
            window
        )

        gestionar_dominios.triggered.connect(
            lambda: self.go_to(1)
        )

        dominios.addAction(
            gestionar_dominios
        )

        # =========================
        # URLS
        # =========================

        urls = menu.addMenu("URLs")

        gestionar_urls = QAction(
            "Gestionar URLs",
            window
        )

        gestionar_urls.triggered.connect(
            lambda: self.go_to(2)
        )

        urls.addAction(
            gestionar_urls
        )

        # =========================
        # INDEXNOW
        # =========================

        indexnow = menu.addMenu("IndexNow")

        enviar_indexnow = QAction(
            "Enviar a IndexNow",
            window
        )

        enviar_indexnow.triggered.connect(
            lambda: self.go_to(3)
        )

        indexnow.addAction(
            enviar_indexnow
        )

        # =========================
        # HERRAMIENTAS
        # =========================

        herramientas = menu.addMenu(
            "Herramientas"
        )

        dashboard = QAction(
            "Dashboard",
            window
        )

        dashboard.triggered.connect(
            lambda: self.go_to(0)
        )

        historial = QAction(
            "Historial",
            window
        )

        historial.triggered.connect(
            lambda: self.go_to(4)
        )

        configuracion = QAction(
            "Configuración",
            window
        )

        configuracion.triggered.connect(
            lambda: self.go_to(5)
        )

        herramientas.addAction(
            dashboard
        )

        herramientas.addAction(
            historial
        )

        herramientas.addAction(
            configuracion
        )

        # =========================
        # AYUDA
        # =========================

        ayuda = menu.addMenu("Ayuda")

        acerca_de = QAction(
            "Acerca de",
            window
        )

        acerca_de.triggered.connect(
            self.show_about
        )

        ayuda.addAction(
            acerca_de
        )

    def go_to(self, index):

        self.window.stack.setCurrentIndex(
            index
        )

        self.window.navigation.setCurrentRow(
            index
        )

    def show_about(self):

        QMessageBox.about(
            self.window,
            "Acerca de BING INDEXER PRO",
            (
                f"<b>{Version.APP_NAME}</b><br><br>"
                f"Versión: {Version.VERSION}<br>"
                f"Autor: {Version.AUTHOR}<br><br>"
                "Herramienta de gestión e indexación "
                "de URLs mediante IndexNow."
            )
        )