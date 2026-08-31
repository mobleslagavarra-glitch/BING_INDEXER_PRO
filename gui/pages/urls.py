from PySide6.QtWidgets import (
    QWidget,
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
    QFileDialog,
)

from services.url_service import UrlService
from services.domain_service import DomainService
from services.excel_import_service import ExcelImportService
from services.indexer_service import IndexerService
from gui.dialogs.url_dialog import UrlDialog


class UrlsPage(QWidget):

    def __init__(self):
        super().__init__()

        self.url_service = UrlService()
        self.domain_service = DomainService()
        self.excel_import_service = ExcelImportService()
        self.indexer_service = IndexerService()

        layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(6)

        self.table.setHorizontalHeaderLabels([
            "ID",
            "Dominio",
            "URL",
            "Estado",
            "Código",
            "Mensaje",
        ])

        self.table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

        self.table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )

        layout.addWidget(self.table)

        botones = QHBoxLayout()

        self.btn_add = QPushButton("➕ Añadir")
        self.btn_edit = QPushButton("✏️ Editar")
        self.btn_delete = QPushButton("🗑️ Eliminar")
        self.btn_import = QPushButton("📥 Importar Excel")
        self.btn_send = QPushButton("🚀 Enviar pendientes")
        self.btn_refresh = QPushButton("🔄 Actualizar")

        botones.addWidget(self.btn_add)
        botones.addWidget(self.btn_edit)
        botones.addWidget(self.btn_delete)
        botones.addWidget(self.btn_import)
        botones.addWidget(self.btn_send)

        botones.addStretch()

        botones.addWidget(self.btn_refresh)

        layout.addLayout(botones)

        self.setLayout(layout)

        self.btn_add.clicked.connect(self.add_url)
        self.btn_edit.clicked.connect(self.edit_url)
        self.btn_delete.clicked.connect(self.delete_url)
        self.btn_import.clicked.connect(self.import_excel)
        self.btn_send.clicked.connect(self.send_pending)
        self.btn_refresh.clicked.connect(self.load_urls)

        self.load_urls()

    def load_urls(self):

        try:

            urls = self.url_service.get_urls()
            domains = self.domain_service.get_domains()

            domain_map = {
                domain.id: domain.domain
                for domain in domains
            }

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

                codigo = (
                    ""
                    if url.response_code is None
                    else str(url.response_code)
                )

                self.table.setItem(
                    row,
                    4,
                    QTableWidgetItem(codigo)
                )

                self.table.setItem(
                    row,
                    5,
                    QTableWidgetItem(
                        url.response_message or ""
                    )
                )

            self.table.resizeColumnsToContents()

        except Exception as error:

            QMessageBox.critical(
                self,
                "Error",
                f"No se pudieron cargar las URLs:\n\n{error}"
            )

    def import_excel(self):

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar archivo Excel",
            "",
            "Archivos Excel (*.xlsx)"
        )

        if not file_path:
            return

        try:

            result = self.excel_import_service.import_file(
                file_path
            )

            QMessageBox.information(
                self,
                "Importación completada",
                (
                    "Importación de Excel completada.\n\n"
                    f"URLs importadas: {result['imported']}\n"
                    f"Duplicadas: {result['duplicates']}\n"
                    f"Inválidas: {result['invalid']}\n"
                    f"Dominios desconocidos/desactivados: "
                    f"{result['unknown_domains']}"
                )
            )

            self.load_urls()

        except Exception as error:

            QMessageBox.critical(
                self,
                "Error al importar",
                f"No se pudo importar el archivo:\n\n{error}"
            )

    def send_pending(self):

        respuesta = QMessageBox.question(
            self,
            "Enviar URLs pendientes",
            (
                "¿Quieres enviar todas las URLs pendientes "
                "a IndexNow?\n\n"
                "El proceso puede tardar si hay muchas URLs."
            ),
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No
        )

        if respuesta != QMessageBox.StandardButton.Yes:
            return

        try:

            results = self.indexer_service.index_pending_urls_batch()

            processed = len(results)

            success = sum(
                1
                for result in results
                if result.status == "ENVIADA"
            )

            errors = sum(
                1
                for result in results
                if result.status == "ERROR"
            )

            QMessageBox.information(
                self,
                "IndexNow",
                (
                    "Proceso de indexación terminado.\n\n"
                    f"Procesadas: {processed}\n"
                    f"Correctas: {success}\n"
                    f"Errores: {errors}"
                )
            )

            self.load_urls()

        except Exception as error:

            QMessageBox.critical(
                self,
                "Error",
                (
                    "Se produjo un error durante "
                    f"la indexación:\n\n{error}"
                )
            )

            self.load_urls()

    def add_url(self):

        domains = self.domain_service.get_domains()

        if not domains:

            QMessageBox.warning(
                self,
                "Sin dominios",
                "Debes crear al menos un dominio antes de añadir una URL."
            )

            return

        dialog = UrlDialog(
            domains,
            self
        )

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        data = dialog.get_data()

        try:

            self.url_service.add_url(
                data["domain_id"],
                data["url"]
            )

            self.load_urls()

        except Exception as error:

            QMessageBox.warning(
                self,
                "No se pudo añadir",
                str(error)
            )

    def edit_url(self):

        row = self.table.currentRow()

        if row < 0:

            QMessageBox.information(
                self,
                "Editar URL",
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
                "Editar URL",
                "La URL ya no existe."
            )

            self.load_urls()
            return

        domains = self.domain_service.get_domains()

        dialog = UrlDialog(
            domains,
            self
        )

        dialog.url_edit.setText(url.url)

        index = dialog.domain_combo.findData(
            url.domain_id
        )

        if index >= 0:
            dialog.domain_combo.setCurrentIndex(index)

        dialog.setWindowTitle("Editar URL")

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        data = dialog.get_data()

        url.domain_id = data["domain_id"]
        url.url = data["url"]

        try:

            self.url_service.update_url(url)

            self.load_urls()

        except Exception as error:

            QMessageBox.warning(
                self,
                "No se pudo actualizar",
                str(error)
            )

    def delete_url(self):

        row = self.table.currentRow()

        if row < 0:

            QMessageBox.information(
                self,
                "Eliminar URL",
                "Selecciona una URL."
            )

            return

        url_id = int(
            self.table.item(row, 0).text()
        )

        respuesta = QMessageBox.question(
            self,
            "Eliminar URL",
            "¿Seguro que quieres eliminar la URL seleccionada?",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No
        )

        if respuesta != QMessageBox.StandardButton.Yes:
            return

        try:

            self.url_service.delete_url(url_id)

            self.load_urls()

        except Exception as error:

            QMessageBox.warning(
                self,
                "No se pudo eliminar",
                str(error)
            )
