from PySide6.QtGui import QAction


class MainMenu:

    def __init__(self, window):

        menu = window.menuBar()

        archivo = menu.addMenu("Archivo")
        dominios = menu.addMenu("Dominios")
        urls = menu.addMenu("URLs")
        indexnow = menu.addMenu("IndexNow")
        herramientas = menu.addMenu("Herramientas")
        ayuda = menu.addMenu("Ayuda")

        salir = QAction("Salir", window)
        salir.triggered.connect(window.close)

        archivo.addAction(salir)