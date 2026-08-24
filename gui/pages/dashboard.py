from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QPushButton,
)

from services.dashboard_service import DashboardService


class DashboardPage(QWidget):

    def __init__(self):
        super().__init__()

        self.service = DashboardService()

        layout = QVBoxLayout()

        titulo = QLabel("📊 Dashboard")
        titulo.setStyleSheet(
            "font-size: 24px; font-weight: bold;"
        )

        layout.addWidget(titulo)

        self.cards_layout = QHBoxLayout()

        self.lbl_domains = self.create_card("🌐 Dominios")
        self.lbl_active = self.create_card("🟢 Activos")
        self.lbl_urls = self.create_card("🔗 URLs")
        self.lbl_pending = self.create_card("⏳ Pendientes")
        self.lbl_success = self.create_card("✅ Correctas")
        self.lbl_errors = self.create_card("❌ Errores")

        layout.addLayout(self.cards_layout)

        automation_frame = QFrame()
        automation_frame.setFrameShape(
            QFrame.Shape.StyledPanel
        )

        automation_layout = QVBoxLayout(
            automation_frame
        )

        automation_title = QLabel(
            "⚙️ Automatización IndexNow"
        )

        automation_title.setStyleSheet(
            "font-size: 18px; font-weight: bold;"
        )

        automation_layout.addWidget(
            automation_title
        )

        self.lbl_automation_status = QLabel(
            "Estado: DESACTIVADA"
        )

        self.lbl_automation_interval = QLabel(
            "Intervalo: -"
        )

        self.lbl_automation_last_run = QLabel(
            "Última ejecución: pendiente"
        )

        self.lbl_automation_processed = QLabel(
            "Procesadas: 0"
        )

        self.lbl_automation_success = QLabel(
            "Correctas: 0"
        )

        self.lbl_automation_errors = QLabel(
            "Errores: 0"
        )

        automation_layout.addWidget(
            self.lbl_automation_status
        )

        automation_layout.addWidget(
            self.lbl_automation_interval
        )

        automation_layout.addWidget(
            self.lbl_automation_last_run
        )

        automation_layout.addWidget(
            self.lbl_automation_processed
        )

        automation_layout.addWidget(
            self.lbl_automation_success
        )

        automation_layout.addWidget(
            self.lbl_automation_errors
        )

        layout.addWidget(
            automation_frame
        )

        self.btn_refresh = QPushButton(
            "🔄 Actualizar"
        )

        self.btn_refresh.clicked.connect(
            self.load_statistics
        )

        layout.addWidget(
            self.btn_refresh
        )

        layout.addStretch()

        self.setLayout(layout)

        self.load_statistics()

    def create_card(self, title):

        frame = QFrame()
        frame.setFrameShape(
            QFrame.Shape.StyledPanel
        )

        card_layout = QVBoxLayout(frame)

        title_label = QLabel(title)

        value_label = QLabel("0")
        value_label.setStyleSheet(
            "font-size: 28px; font-weight: bold;"
        )

        value_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        card_layout.addWidget(title_label)
        card_layout.addWidget(value_label)

        self.cards_layout.addWidget(frame)

        return value_label

    def update_automation_status(
        self,
        enabled,
        interval_minutes,
        last_run=None,
        processed=0,
        success=0,
        errors=0
    ):

        if enabled:

            self.lbl_automation_status.setText(
                "Estado: ACTIVA"
            )

        else:

            self.lbl_automation_status.setText(
                "Estado: DESACTIVADA"
            )

        self.lbl_automation_interval.setText(
            f"Intervalo: {interval_minutes} minuto(s)"
        )

        if last_run is None:

            ultima = "pendiente"

        else:

            ultima = last_run.strftime(
                "%H:%M:%S"
            )

        self.lbl_automation_last_run.setText(
            f"Última ejecución: {ultima}"
        )

        self.lbl_automation_processed.setText(
            f"Procesadas: {processed}"
        )

        self.lbl_automation_success.setText(
            f"Correctas: {success}"
        )

        self.lbl_automation_errors.setText(
            f"Errores: {errors}"
        )

    def load_statistics(self):

        try:

            statistics = self.service.get_statistics()

            self.lbl_domains.setText(
                str(statistics["total_domains"])
            )

            self.lbl_active.setText(
                str(statistics["active_domains"])
            )

            self.lbl_urls.setText(
                str(statistics["total_urls"])
            )

            self.lbl_pending.setText(
                str(statistics["pending_urls"])
            )

            self.lbl_success.setText(
                str(statistics["successful_urls"])
            )

            self.lbl_errors.setText(
                str(statistics["error_urls"])
            )

        except Exception as error:

            print(
                f"Error cargando estadísticas: {error}"
            )
