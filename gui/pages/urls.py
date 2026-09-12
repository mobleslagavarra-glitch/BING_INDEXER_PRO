from PySide6.QtCore import (
    QObject,
    QThread,
    Signal,
    Qt,
    QAbstractTableModel,
    QModelIndex,
)

from PySide6.QtWidgets import (
    QWidget,
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTableView,
    QTableWidgetItem,
    QMessageBox,
    QFileDialog,
    QHeaderView,
)

from services.url_service import UrlService
from services.domain_service import DomainService
from services.excel_import_service import ExcelImportService
from services.indexer_service import IndexerService
from gui.dialogs.url_dialog import UrlDialog


class IndexingWorker(QObject):

    finished = Signal(object)
    error = Signal(str)

    def __init__(self, indexer_service):
        super().__init__()
        self.indexer_service = indexer_service

    def run(self):

        try:
            results = self.indexer_service.index_pending_urls_batch()
            self.finished.emit(results)

        except Exception as error:
            self.error.emit(str(error))


class ExcelImportWorker(QObject):

    finished = Signal(object)
    error = Signal(str)

    def __init__(self, excel_import_service, file_path):
        super().__init__()
        self.excel_import_service = excel_import_service
        self.file_path = file_path

    def run(self):
        try:
            result = self.excel_import_service.import_file(
                self.file_path
            )
            self.finished.emit(result)

        except Exception as error:
            self.error.emit(str(error))


class UrlsTableModel(QAbstractTableModel):
    HEADERS = [
        "ID",
        "Dominio",
        "URL",
        "Estado",
        "Código",
        "Mensaje",
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self._rows = []

    def rowCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return len(self._rows)

    def columnCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return len(self.HEADERS)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None

        if role != Qt.ItemDataRole.DisplayRole:
            return None

        row = index.row()
        column = index.column()

        if row < 0 or row >= len(self._rows):
            return None

        if column < 0 or column >= len(self.HEADERS):
            return None

        return self._rows[row][column]

    def headerData(
        self,
        section,
        orientation,
        role=Qt.ItemDataRole.DisplayRole,
    ):
        if role != Qt.ItemDataRole.DisplayRole:
            return None

        if orientation == Qt.Orientation.Horizontal:
            if 0 <= section < len(self.HEADERS):
                return self.HEADERS[section]

        return None

    def set_rows(self, rows):
        self.beginResetModel()
        self._rows = rows
        self.endResetModel()


class UrlsTableView(QTableView):
    """
    QTableView optimizada con una pequeña capa de compatibilidad
    para mantener las operaciones que utilizaba QTableWidget:
    rowCount(), columnCount(), item(), currentRow(),
    horizontalHeaderItem() y selectRow().
    """

    def rowCount(self):
        model = self.model()
        return model.rowCount() if model is not None else 0

    def columnCount(self):
        model = self.model()
        return model.columnCount() if model is not None else 0

    def item(self, row, column):
        model = self.model()

        if model is None:
            return None

        if row < 0 or row >= model.rowCount():
            return None

        if column < 0 or column >= model.columnCount():
            return None

        index = model.index(row, column)

        if not index.isValid():
            return None

        value = model.data(
            index,
            Qt.ItemDataRole.DisplayRole,
        )

        if value is None:
            return None

        return QTableWidgetItem(str(value))

    def currentRow(self):
        index = self.currentIndex()

        if not index.isValid():
            return -1

        return index.row()

    def selectRow(self, row):
        model = self.model()

        if model is None:
            return

        if row < 0 or row >= model.rowCount():
            return

        index = model.index(row, 0)

        self.setCurrentIndex(index)

        selection_model = self.selectionModel()

        if selection_model is not None:
            selection_model.select(
                index,
                selection_model.SelectionFlag.ClearAndSelect
                | selection_model.SelectionFlag.Rows,
            )

    def horizontalHeaderItem(self, column):
        model = self.model()

        if model is None:
            return None

        if column < 0 or column >= model.columnCount():
            return None

        value = model.headerData(
            column,
            Qt.Orientation.Horizontal,
            Qt.ItemDataRole.DisplayRole,
        )

        if value is None:
            return None

        return QTableWidgetItem(str(value))


class UrlsPage(QWidget):

    def __init__(self):
        super().__init__()

        self.url_service = UrlService()
        self.domain_service = DomainService()
        self.excel_import_service = ExcelImportService()
        self.indexer_service = IndexerService()

        self._excel_thread = None
        self._excel_worker = None

        self._index_thread = None
        self._index_worker = None

        layout = QVBoxLayout()

        self.table_model = UrlsTableModel(self)
        self.table = UrlsTableView()
        self.table.setModel(self.table_model)

        self.table.setEditTriggers(
            QTableView.EditTrigger.NoEditTriggers
        )

        self.table.setSelectionBehavior(
            QTableView.SelectionBehavior.SelectRows
        )

        self.table.setSelectionMode(
            QTableView.SelectionMode.ExtendedSelection
        )

        # Optimización para grandes cantidades de URLs.
        self.table.setSortingEnabled(False)

        header = self.table.horizontalHeader()

        for column in range(6):
            header.setSectionResizeMode(
                column,
                QHeaderView.ResizeMode.Fixed
            )

        # Optimización de renderizado para miles de filas.
        # Evita cálculos innecesarios de ajuste de texto y altura
        # individual de las filas.
        self.table.setWordWrap(False)

        vertical_header = self.table.verticalHeader()
        vertical_header.setSectionResizeMode(
            QHeaderView.ResizeMode.Fixed
        )

        self.table.setColumnWidth(0, 70)
        self.table.setColumnWidth(1, 180)
        self.table.setColumnWidth(2, 500)
        self.table.setColumnWidth(3, 110)
        self.table.setColumnWidth(4, 80)
        self.table.setColumnWidth(5, 350)

        layout.addWidget(self.table)

        botones = QHBoxLayout()

        self.btn_add = QPushButton("➕ Añadir")
        self.btn_edit = QPushButton("✏️ Editar")
        self.btn_delete = QPushButton("🗑️ Eliminar")
        self.btn_import = QPushButton("📥 Importar Excel")
        self.btn_send = QPushButton("🚀 Enviar pendientes")
        self.btn_reset_sent = QPushButton(
            "🔁 Marcar enviadas como pendientes"
        )
        self.btn_refresh = QPushButton("🔄 Actualizar")

        botones.addWidget(self.btn_add)
        botones.addWidget(self.btn_edit)
        botones.addWidget(self.btn_delete)
        botones.addWidget(self.btn_import)
        botones.addWidget(self.btn_send)
        botones.addWidget(self.btn_reset_sent)

        botones.addStretch()

        botones.addWidget(self.btn_refresh)

        layout.addLayout(botones)

        self.setLayout(layout)

        self.btn_add.clicked.connect(self.add_url)
        self.btn_edit.clicked.connect(self.edit_url)
        self.btn_delete.clicked.connect(self.delete_url)
        self.btn_import.clicked.connect(self.import_excel)
        self.btn_send.clicked.connect(self.send_pending)
        self.btn_reset_sent.clicked.connect(
            self.reset_sent_urls
        )
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

            rows = []

            for url in urls:

                codigo = (
                    ""
                    if url.response_code is None
                    else str(url.response_code)
                )

                rows.append((
                    str(url.id),
                    domain_map.get(url.domain_id, ""),
                    url.url,
                    url.status,
                    codigo,
                    url.response_message or "",
                ))

            # Evitar repintados durante la sustitución del modelo.
            self.table.setUpdatesEnabled(False)
            self.table.blockSignals(True)
            self.table.setSortingEnabled(False)

            try:
                self.table_model.set_rows(rows)
            finally:
                self.table.blockSignals(False)
                self.table.setUpdatesEnabled(True)

        except Exception as error:

            QMessageBox.critical(
                self,
                "Error",
                f"No se pudieron cargar las URLs:\n\n{error}"
            )

    def import_excel(self):

        if (
            hasattr(self, "_excel_thread")
            and self._excel_thread is not None
            and self._excel_thread.isRunning()
        ):
            QMessageBox.information(
                self,
                "Importaci?n Excel",
                "Ya hay una importaci?n en ejecuci?n."
            )
            return

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar archivo Excel",
            "",
            "Archivos Excel (*.xlsx)"
        )

        if not file_path:
            return

        self.btn_import.setEnabled(False)
        self.btn_send.setEnabled(False)
        self.btn_add.setEnabled(False)
        self.btn_edit.setEnabled(False)
        self.btn_delete.setEnabled(False)
        self.btn_reset_sent.setEnabled(False)
        self.btn_refresh.setEnabled(False)

        self.btn_import.setText("? Importando...")

        self._excel_thread = QThread(self)

        self._excel_worker = ExcelImportWorker(
            self.excel_import_service,
            file_path
        )

        self._excel_worker.moveToThread(
            self._excel_thread
        )

        self._excel_thread.started.connect(
            self._excel_worker.run
        )

        self._excel_worker.finished.connect(
            self._excel_import_finished
        )

        self._excel_worker.error.connect(
            self._excel_import_error
        )

        self._excel_worker.finished.connect(
            self._excel_thread.quit
        )

        self._excel_worker.error.connect(
            self._excel_thread.quit
        )

        self._excel_thread.finished.connect(
            self._excel_thread_finished
        )

        self._excel_thread.start()

    def _excel_import_finished(self, result):

        try:
            self.load_urls()

            QMessageBox.information(
                self,
                "Importaci?n completada",
                (
                    "Importaci?n de Excel completada.\n\n"
                    f"URLs importadas: {result['imported']}\n"
                    f"Duplicadas: {result['duplicates']}\n"
                    f"Inv?lidas: {result['invalid']}\n"
                    f"Dominios desconocidos/desactivados: "
                    f"{result['unknown_domains']}"
                )
            )

        except Exception as error:
            QMessageBox.critical(
                self,
                "Error",
                f"No se pudieron actualizar las URLs:\n\n{error}"
            )

    def _excel_import_error(self, error_message):

        QMessageBox.critical(
            self,
            "Error al importar",
            (
                "No se pudo importar el archivo:\n\n"
                f"{error_message}"
            )
        )

    def _excel_thread_finished(self):

        self.btn_import.setEnabled(True)
        self.btn_send.setEnabled(True)
        self.btn_add.setEnabled(True)
        self.btn_edit.setEnabled(True)
        self.btn_delete.setEnabled(True)
        self.btn_reset_sent.setEnabled(True)
        self.btn_refresh.setEnabled(True)

        self.btn_import.setText("?? Importar Excel")

        if self._excel_worker is not None:
            self._excel_worker.deleteLater()

        if self._excel_thread is not None:
            self._excel_thread.deleteLater()

        self._excel_worker = None
        self._excel_thread = None

    def send_pending(self):

        respuesta = QMessageBox.question(
            self,
            "Enviar URLs pendientes",
            (
                "?Quieres enviar todas las URLs pendientes "
                "a IndexNow?\n\n"
                "El proceso se ejecutar? en segundo plano "
                "para que la aplicaci?n siga respondiendo."
            ),
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No
        )

        if respuesta != QMessageBox.StandardButton.Yes:
            return

        if (
            hasattr(self, "_index_thread")
            and self._index_thread is not None
            and self._index_thread.isRunning()
        ):
            QMessageBox.information(
                self,
                "IndexNow",
                "Ya hay un proceso de indexaci?n en ejecuci?n."
            )
            return

        self.btn_send.setEnabled(False)
        self.btn_import.setEnabled(False)
        self.btn_add.setEnabled(False)
        self.btn_edit.setEnabled(False)
        self.btn_delete.setEnabled(False)
        self.btn_reset_sent.setEnabled(False)
        self.btn_refresh.setEnabled(False)

        self.btn_send.setText("? Indexando...")

        self._index_thread = QThread(self)

        self._index_worker = IndexingWorker(
            self.indexer_service
        )

        self._index_worker.moveToThread(
            self._index_thread
        )

        self._index_thread.started.connect(
            self._index_worker.run
        )

        self._index_worker.finished.connect(
            self._indexing_finished
        )

        self._index_worker.error.connect(
            self._indexing_error
        )

        self._index_worker.finished.connect(
            self._index_thread.quit
        )

        self._index_worker.error.connect(
            self._index_thread.quit
        )

        self._index_thread.finished.connect(
            self._indexing_thread_finished
        )

        self._index_thread.start()

    def _indexing_finished(self, results):

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

        self.load_urls()

        QMessageBox.information(
            self,
            "IndexNow",
            (
                "Proceso de indexaci?n terminado.\n\n"
                f"Procesadas: {processed}\n"
                f"Correctas: {success}\n"
                f"Errores: {errors}"
            )
        )

    def _indexing_error(self, error_message):

        QMessageBox.critical(
            self,
            "Error de IndexNow",
            (
                "Se produjo un error durante "
                "la indexaci?n:\n\n"
                f"{error_message}"
            )
        )

        self.load_urls()

    def _indexing_thread_finished(self):

        self.btn_send.setEnabled(True)
        self.btn_import.setEnabled(True)
        self.btn_add.setEnabled(True)
        self.btn_edit.setEnabled(True)
        self.btn_delete.setEnabled(True)
        self.btn_reset_sent.setEnabled(True)
        self.btn_refresh.setEnabled(True)

        self.btn_send.setText("?? Enviar pendientes")

        if self._index_worker is not None:
            self._index_worker.deleteLater()

        if self._index_thread is not None:
            self._index_thread.deleteLater()

        self._index_worker = None
        self._index_thread = None


    def reset_sent_urls(self):

        selected_rows = sorted({
            index.row()
            for index in self.table.selectionModel().selectedRows()
        })

        if not selected_rows:
            QMessageBox.information(
                self,
                "Marcar como pendientes",
                "Selecciona una o varias URLs."
            )
            return

        try:

            urls = []

            for row in selected_rows:

                item = self.table.item(row, 0)

                if item is None:
                    continue

                url_id = int(item.text())
                url = self.url_service.get_url(url_id)

                if url is not None:
                    urls.append(url)

            reset_urls = [
                url
                for url in urls
                if url.status in ("ENVIADA", "ERROR")
            ]

            if not reset_urls:
                QMessageBox.information(
                    self,
                    "Marcar como pendientes",
                    "Ninguna de las URLs seleccionadas est? en estado ENVIADA o ERROR."
                )
                return

            cantidad = len(reset_urls)

            respuesta = QMessageBox.question(
                self,
                "Marcar como pendientes",
                (
                    f"?Quieres marcar {cantidad} URL"
                    f"{'s' if cantidad != 1 else ''} como PENDIENTE "
                    "para poder enviarla"
                    f"{'s' if cantidad != 1 else ''} de nuevo?"
                ),
                QMessageBox.StandardButton.Yes
                | QMessageBox.StandardButton.No
            )

            if respuesta != QMessageBox.StandardButton.Yes:
                return

            for url in reset_urls:

                url.status = "PENDIENTE"
                url.response_code = None
                url.response_message = ""

                self.url_service.update_url(url)

            self.load_urls()

            QMessageBox.information(
                self,
                "URLs actualizadas",
                (
                    f"Se han marcado {cantidad} URL"
                    f"{'s' if cantidad != 1 else ''} como PENDIENTE."
                )
            )

        except Exception as error:

            QMessageBox.warning(
                self,
                "No se pudieron actualizar",
                (
                    "No se pudieron marcar las URLs como pendientes:"
                    f"\n\n{error}"
                )
            )

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
