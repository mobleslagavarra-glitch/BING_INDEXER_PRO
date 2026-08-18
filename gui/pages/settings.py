from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QPushButton,
)


from core.version import Version


class SettingsPage(QWidget):

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        titulo = QLabel("Configuracion")
        titulo.setStyleSheet(
            "font-size: 24px; font-weight: bold;"
        )

        layout.addWidget(titulo)

        info_frame = QFrame()
        info_frame.setFrameShape(
            QFrame.Shape.StyledPanel
        )

        info_layout = QVBoxLayout(info_frame)

        self.lbl_app = QLabel()
        self.lbl_version = QLabel()
        self.lbl_author = QLabel()
        self.lbl_status = QLabel()

        info_layout.addWidget(self.lbl_app)
        info_layout.addWidget(self.lbl_version)
        info_layout.addWidget(self.lbl_author)
        info_layout.addWidget(self.lbl_status)

        layout.addWidget(info_frame)

        botones = QHBoxLayout()

        botones.addStretch()

        self.btn_refresh = QPushButton(
            "Actualizar informacion"
        )

        botones.addWidget(self.btn_refresh)

        layout.addLayout(botones)

        layout.addStretch()

        self.setLayout(layout)

        self.btn_refresh.clicked.connect(
            self.load_information
        )

        self.load_information()

    def load_information(self):

        self.lbl_app.setText(
            f"Aplicacion: {Version.APP_NAME}"
        )

        self.lbl_version.setText(
            f"Version: {Version.VERSION}"
        )

        self.lbl_author.setText(
            f"Autor: {Version.AUTHOR}"
        )

        self.lbl_status.setText(
            "Estado: Aplicacion operativa"
        )