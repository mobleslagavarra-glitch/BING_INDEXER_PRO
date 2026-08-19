from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QPushButton,
    QCheckBox,
    QSpinBox,
    QMessageBox,
)

from core.version import Version
from services.settings_service import SettingsService


class SettingsPage(QWidget):

    def __init__(self):
        super().__init__()

        self.settings_service = SettingsService()

        layout = QVBoxLayout()

        titulo = QLabel("Configuración")
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

        indexnow_frame = QFrame()
        indexnow_frame.setFrameShape(
            QFrame.Shape.StyledPanel
        )

        indexnow_layout = QVBoxLayout(indexnow_frame)

        titulo_indexnow = QLabel("Configuración de IndexNow")
        titulo_indexnow.setStyleSheet(
            "font-size: 18px; font-weight: bold;"
        )

        indexnow_layout.addWidget(titulo_indexnow)

        self.chk_auto = QCheckBox(
            "Envío automático a IndexNow"
        )

        indexnow_layout.addWidget(self.chk_auto)

        reintentos_layout = QHBoxLayout()

        lbl_reintentos = QLabel(
            "Número de reintentos:"
        )

        self.spin_retries = QSpinBox()
        self.spin_retries.setMinimum(0)
        self.spin_retries.setMaximum(10)

        reintentos_layout.addWidget(lbl_reintentos)
        reintentos_layout.addWidget(self.spin_retries)
        reintentos_layout.addStretch()

        indexnow_layout.addLayout(reintentos_layout)

        layout.addWidget(indexnow_frame)

        botones = QHBoxLayout()

        botones.addStretch()

        self.btn_save = QPushButton(
            "💾 Guardar configuración"
        )

        self.btn_refresh = QPushButton(
            "🔄 Actualizar información"
        )

        botones.addWidget(self.btn_save)
        botones.addWidget(self.btn_refresh)

        layout.addLayout(botones)

        layout.addStretch()

        self.setLayout(layout)

        self.btn_save.clicked.connect(
            self.save_settings
        )

        self.btn_refresh.clicked.connect(
            self.load_information
        )

        self.load_information()

    def load_information(self):

        self.lbl_app.setText(
            f"Aplicación: {Version.APP_NAME}"
        )

        self.lbl_version.setText(
            f"Versión: {Version.VERSION}"
        )

        self.lbl_author.setText(
            f"Autor: {Version.AUTHOR}"
        )

        self.lbl_status.setText(
            "Estado: Aplicación operativa"
        )

        try:

            self.settings_service.initialize_defaults()

            auto = self.settings_service.get(
                "indexnow_auto",
                "0"
            )

            retries = self.settings_service.get(
                "indexnow_retries",
                "3"
            )

            self.chk_auto.setChecked(
                str(auto) == "1"
            )

            self.spin_retries.setValue(
                int(retries)
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Error",
                f"No se pudo cargar la configuración:\n\n{error}"
            )

    def save_settings(self):

        try:

            auto = (
                "1"
                if self.chk_auto.isChecked()
                else "0"
            )

            retries = str(
                self.spin_retries.value()
            )

            self.settings_service.set(
                "indexnow_auto",
                auto
            )

            self.settings_service.set(
                "indexnow_retries",
                retries
            )

            QMessageBox.information(
                self,
                "Configuración guardada",
                "La configuración se ha guardado correctamente."
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Error",
                f"No se pudo guardar la configuración:\n\n{error}"
            )
