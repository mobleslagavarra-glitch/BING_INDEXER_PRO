from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QWidget, QVBoxLayout


class Dashboard(QWidget):

    def __init__(self):

        super().__init__()

        layout = QVBoxLayout()

        titulo = QLabel("BING INDEXER PRO")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitulo = QLabel("Panel principal")
        subtitulo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addStretch()
        layout.addWidget(titulo)
        layout.addWidget(subtitulo)
        layout.addStretch()

        self.setLayout(layout)