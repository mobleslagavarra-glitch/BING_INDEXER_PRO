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
from services.indexer_service import IndexerService


class IndexNowPage(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.url_service = UrlService()
        self.domain_service = DomainService()
        self.indexer_service = IndexerService()

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

        self.table.setColumnWidth(0, 60)
        self.table.setColumnWidth(1, 180)
        self.table.setColumnWidth(2, 500)
        self.table.setColumnWidth(3, 120)
        self.table.setColumnWidth(4, 80)

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

        if url_record.status == "ENVIADA":

            QMessageBox.information(
                self,
                "IndexNow",
                (
                    "Esta URL ya ha sido enviada correctamente "
                    "a IndexNow.\n\n"
                    f"URL: {url_record.url}\n"
                    f"Código HTTP: {url_record.response_code}"
                )
            )

            return

        try:

            result = self.indexer_service.index_url(
                url_id
            )

            if result.status == "ENVIADA":

                QMessageBox.information(
                    self,
                    "IndexNow",
                    (
                        "La URL ha sido enviada "
                        "correctamente a IndexNow.\n\n"
                        f"URL: {result.url}\n"
                        f"Código HTTP: {result.response_code}"
                    )
                )

            else:

                QMessageBox.warning(
                    self,
                    "IndexNow",
                    (
                        "IndexNow no ha podido aceptar "
                        "la URL.\n\n"
                        f"URL: {result.url}\n"
                        f"Código: {result.response_code}\n"
                        f"Mensaje: {result.response_message}"
                    )
                )

            self.load_urls()

        except ValueError as error:

            QMessageBox.warning(
                self,
                "IndexNow",
                str(error)
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
