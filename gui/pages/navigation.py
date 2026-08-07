from PySide6.QtWidgets import QListWidget


class Navigation(QListWidget):

    def __init__(self):
        super().__init__()

        self.addItems([
            "🏠 Dashboard",
            "🌍 Dominios",
            "🔗 URLs",
            "📄 Historial",
            "⚙ Configuración"
        ])

        self.setMaximumWidth(220)
        self.setCurrentRow(0)