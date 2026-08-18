from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QMessageBox,
    QLabel,
)

from services.url_service import UrlService
from services.domain_service import DomainService
from services.indexnow_service import IndexNowService
from services.history_service import HistoryService


class IndexNowPage(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.url_service = UrlService()
        self.domain_service = DomainService()
        self.indexnow_service = IndexNowService()
        self.history_service = HistoryService()

        self.setup_ui()
        self.load_urls()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("IndexNow")
        title.setStyleSheet(
            "font-size: 22px; font-weight: bold;"
        )

        layout.addWidget(title)

        info = QLabel(
            "URLs pendientes o con error disponibles para enviar a IndexNow."
        )

        layout.addWidget(info)

        self.table = QTableWidget()

        self.table.setColumnCount(5)

        self.table.setHorizontalHeaderLabels([
            "ID",
            "Dominio",
            "URL",
            "Estado",
            "Código"
        ])

        self.table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )

        self.table.setSelectionMode(
            QTableWidget.SelectionMode.SingleSelection
        )

        self.table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

        self.table.horizontalHeader().setStretchLastSection(True)

        layout.addWidget(self.table)

        buttons_layout = QHBoxLayout()

        self.send_button = QPushButton(
            "Enviar a IndexNow"
        )

        self.refresh_button = QPushButton(
            "Actualizar"
        )

        buttons_layout.addWidget(
            self.send_button
        )

        buttons_layout.addWidget(
            self.refresh_button
        )

        buttons_layout.addStretch()

        layout.addLayout(buttons_layout)

        self.send_button.clicked.connect(
            self.send_selected_url
        )

        self.refresh_button.clicked.connect(
            self.load_urls
        )

    def load_urls(self):

        self.table.setRowCount(0)

        urls = self.url_service.get_urls()
        domains = self.domain_service.get_domains()

        domains_by_id = {
            domain.id: domain
            for domain in domains
        }

        for url in urls:

            domain = domains_by_id.get(
                url.domain_id
            )

            if domain is None:
                continue

            if not domain.enabled:
                continue

            if not domain.api_key:
                continue

            if url.status not in (
                "PENDIENTE",
                "ERROR",
            ):
                continue

            row = self.table.rowCount()

            self.table.insertRow(row)

            self.table.setItem(
                row,
                0,
                QTableWidgetItem(
                    str(url.id)
                )
            )

            self.table.setItem(
                row,
                1,
                QTableWidgetItem(
                    domain.domain
                )
            )

            self.table.setItem(
                row,
                2,
                QTableWidgetItem(
                    url.url
                )
            )

            self.table.setItem(
                row,
                3,
                QTableWidgetItem(
                    url.status
                )
            )

            codigo = ""

            if url.response_code is not None:
                codigo = str(url.response_code)

            self.table.setItem(
                row,
                4,
                QTableWidgetItem(
                    codigo
                )
            )

        self.table.resizeColumnsToContents()

        self.send_button.setEnabled(
            self.table.rowCount() > 0
        )

    def send_selected_url(self):

        selected_rows = (
            self.table.selectionModel()
            .selectedRows()
        )

        if not selected_rows:

            QMessageBox.warning(
                self,
                "IndexNow",
                "Selecciona una URL para enviarla a IndexNow."
            )

            return

        row = selected_rows[0].row()

        id_item = self.table.item(row, 0)

        if id_item is None:
            return

        try:

            url_id = int(
                id_item.text()
            )

        except ValueError:

            QMessageBox.critical(
                self,
                "Error",
                "El ID de la URL no es válido."
            )

            return

        url_record = self.url_service.get_url(
            url_id
        )

        if url_record is None:

            QMessageBox.critical(
                self,
                "Error",
                "No se ha encontrado la URL."
            )

            return

        domain = self.domain_service.get_domain(
            url_record.domain_id
        )

        if domain is None:

            QMessageBox.critical(
                self,
                "Error",
                "No se ha encontrado el dominio asociado."
            )

            return

        if not domain.api_key:

            QMessageBox.warning(
                self,
                "IndexNow",
                "El dominio no tiene API Key configurada."
            )

            return

        # Normalizar la URL antes de enviarla.
        normalized_url = self.url_service._normalize_url(
            url_record.url
        )

        # Si la URL estaba guardada en formato Markdown,
        # actualizar también el registro de la base de datos.
        if normalized_url != url_record.url:
            url_record.url = normalized_url
            self.url_service.update_url(
                url_record
            )

        try:

            result = self.indexnow_service.submit(
                domain.domain,
                domain.api_key,
                normalized_url
            )

            if result.get("success"):

                url_record.status = "ENVIADA"

                url_record.response_code = (
                    result.get("status_code")
                )

                url_record.response_message = (
                    result.get(
                        "message",
                        "Solicitud aceptada por IndexNow"
                    )
                )

                self.url_service.update_url(
                    url_record
                )

                self.history_service.add(
                    "INDEXACION_COMPLETADA",
                    (
                        f"URL enviada correctamente: "
                        f"{normalized_url}"
                    )
                )

                QMessageBox.information(
                    self,
                    "IndexNow",
                    (
                        "La URL ha sido enviada "
                        "correctamente a IndexNow."
                    )
                )

                self.load_urls()

                return

            url_record.status = "ERROR"

            url_record.response_code = (
                result.get("status_code")
            )

            url_record.response_message = (
                result.get(
                    "message",
                    "Error al enviar la URL a IndexNow"
                )
            )

            self.url_service.update_url(
                url_record
            )

            self.history_service.add(
                "ERROR_INDEXACION",
                (
                    f"Error al enviar URL: "
                    f"{normalized_url} - "
                    f"{url_record.response_message}"
                )
            )

            QMessageBox.warning(
                self,
                "IndexNow",
                (
                    "IndexNow ha rechazado la solicitud.\n\n"
                    f"Código: {url_record.response_code}\n"
                    f"Mensaje: {url_record.response_message}"
                )
            )

            self.load_urls()

        except Exception as error:

            QMessageBox.critical(
                self,
                "Error",
                (
                    "Se ha producido un error al enviar "
                    f"la URL a IndexNow:\n\n{error}"
                )
            )

            self.load_urls()