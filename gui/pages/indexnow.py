from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
)

from services.url_service import UrlService
from services.domain_service import DomainService
from services.indexnow_service import IndexNowService
from services.history_service import HistoryService


class IndexNowPage(QWidget):

    def __init__(self):
        super().__init__()

        self.url_service = UrlService()
        self.domain_service = DomainService()
        self.indexnow_service = IndexNowService()
        self.history_service = HistoryService()

        layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(4)

        self.table.setHorizontalHeaderLabels([
            "ID",
            "Dominio",
            "URL",
            "Estado",
        ])

        self.table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

        self.table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )

        layout.addWidget(self.table)

        botones = QHBoxLayout()

        self.btn_send = QPushButton("Enviar a IndexNow")
        self.btn_refresh = QPushButton("Actualizar")

        botones.addWidget(self.btn_send)
        botones.addStretch()
        botones.addWidget(self.btn_refresh)

        layout.addLayout(botones)

        self.setLayout(layout)

        self.btn_send.clicked.connect(
            self.send_to_indexnow
        )

        self.btn_refresh.clicked.connect(
            self.load_urls
        )

        self.load_urls()

    def load_urls(self):

        try:

            urls = self.url_service.get_urls()
            domains = self.domain_service.get_domains()

            domain_map = {
                domain.id: domain.domain
                for domain in domains
            }

            # Solo mostrar URLs pendientes o con error
            # cuyo dominio tenga API key configurada.
            valid_domain_ids = {
                domain.id
                for domain in domains
                if domain.api_key
            }

            urls = [
                url
                for url in urls
                if (
                    url.status in ("PENDIENTE", "ERROR")
                    and url.domain_id in valid_domain_ids
                )
            ]

            self.table.setRowCount(len(urls))

            for row, url in enumerate(urls):

                self.table.setItem(
                    row,
                    0,
                    QTableWidgetItem(str(url.id))
                )

                self.table.setItem(
                    row,
                    1,
                    QTableWidgetItem(
                        domain_map.get(
                            url.domain_id,
                            ""
                        )
                    )
                )

                self.table.setItem(
                    row,
                    2,
                    QTableWidgetItem(url.url)
                )

                self.table.setItem(
                    row,
                    3,
                    QTableWidgetItem(url.status)
                )

            self.table.resizeColumnsToContents()

        except Exception as error:

            QMessageBox.critical(
                self,
                "Error",
                f"No se pudieron cargar las URLs:\n\n{error}"
            )

    def send_to_indexnow(self):

        row = self.table.currentRow()

        if row < 0:
            QMessageBox.information(
                self,
                "IndexNow",
                "Selecciona una URL."
            )
            return

        url_id = int(
            self.table.item(row, 0).text()
        )

        url = self.url_service.get_url(url_id)

        if url is None:
            QMessageBox.warning(
                self,
                "IndexNow",
                "La URL ya no existe."
            )
            self.load_urls()
            return

        domain = next(
            (
                item
                for item in self.domain_service.get_domains()
                if item.id == url.domain_id
            ),
            None
        )

        if domain is None:
            QMessageBox.warning(
                self,
                "IndexNow",
                "No se encontró el dominio asociado."
            )
            return

        if not domain.api_key:
            QMessageBox.warning(
                self,
                "IndexNow",
                "El dominio no tiene una API key configurada."
            )
            return

        try:

            result = self.indexnow_service.submit(
                domain.domain,
                domain.api_key,
                url.url
            )

            status_code = result.get("status_code")
            message = result.get("message", "")

            if status_code in (200, 202):

                url.status = "ENVIADA"
                url.response_code = status_code
                url.response_message = (
                    message
                    if message
                    else "Solicitud aceptada por IndexNow"
                )

                self.url_service.update_url(url)

                self.history_service.add(
                    "INDEXACION_COMPLETADA",
                    (
                        f"URL enviada correctamente: {url.url} "
                        f"(HTTP {status_code})"
                    )
                )

                self.load_urls()

                QMessageBox.information(
                    self,
                    "IndexNow",
                    (
                        "URL enviada correctamente.\n\n"
                        f"Código: {status_code}\n\n"
                        f"Respuesta: "
                        f"{message or '(sin contenido)'}"
                    )
                )

                return

            url.status = "ERROR"
            url.response_code = status_code
            url.response_message = (
                message or "IndexNow rechazó la solicitud"
            )

            self.url_service.update_url(url)

            self.history_service.add(
                "INDEXACION_ERROR",
                (
                    f"Error indexando {url.url}: "
                    f"HTTP {status_code} - "
                    f"{message or 'sin contenido'}"
                )
            )

            self.load_urls()

            QMessageBox.warning(
                self,
                "Error IndexNow",
                (
                    f"Código: {status_code}\n\n"
                    f"Respuesta:\n"
                    f"{message or '(sin contenido)'}"
                )
            )

        except Exception as error:

            url.status = "ERROR"
            url.response_code = None
            url.response_message = str(error)

            try:

                self.url_service.update_url(url)

                self.history_service.add(
                    "INDEXACION_ERROR",
                    f"Error indexando {url.url}: {error}"
                )

            except Exception:
                pass

            self.load_urls()

            QMessageBox.critical(
                self,
                "Error IndexNow",
                str(error)
            )