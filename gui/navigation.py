from PySide6.QtWidgets import QListWidget


class Navigation(QListWidget):

    def __init__(self):

        super().__init__()

        self.addItem("🏠 Dashboard")
        self.addItem("🌍 Dominios")
        self.addItem("🔗 URLs")
        self.addItem("📤 IndexNow")
        self.addItem("📄 Historial")
        self.addItem("⚙ Configuración")

        self.setMaximumWidth(220)