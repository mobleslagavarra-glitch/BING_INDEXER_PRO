from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QLabel,
    QMessageBox,
)

from services.history_service import HistoryService


class HistoryPage(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.service = HistoryService()

        self.setup_ui()
        self.load_history()

    def setup_ui(self):

        layout = QVBoxLayout(self)

        titulo = QLabel("Historial")
        titulo.setStyleSheet(
            "font-size: 22px; font-weight: bold;"
        )

        layout.addWidget(titulo)

        info = QLabel(
            "Registro de las operaciones realizadas por BING_INDEXER_PRO."
        )

        layout.addWidget(info)

        self.table = QTableWidget()
        self.table.setColumnCount(7)

        self.table.setHorizontalHeaderLabels([
            "ID",
            "Fecha / Hora",
            "Tipo",
            "Descripción",
            "Procesadas",
            "Correctas",
            "Errores",
        ])

        self.table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

        self.table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )

        self.table.setSelectionMode(
            QTableWidget.SelectionMode.SingleSelection
        )

        self.table.setAlternatingRowColors(True)

        layout.addWidget(self.table)

        botones = QHBoxLayout()

        self.btn_clear = QPushButton(
            "Limpiar historial"
        )

        self.btn_refresh = QPushButton(
            "Actualizar"
        )

        botones.addWidget(self.btn_clear)
        botones.addStretch()
        botones.addWidget(self.btn_refresh)

        layout.addLayout(botones)

        self.btn_refresh.clicked.connect(
            self.load_history
        )

        self.btn_clear.clicked.connect(
            self.clear_history
        )

    def load_history(self):

        try:

            history = self.service.get_all()

            self.table.setRowCount(
                len(history)
            )

            for row, event in enumerate(history):

                event_id = event[0]
                event_date = event[1]
                event_type = event[2]
                description = event[3]
                processed_count = event[4]
                success_count = event[5]
                error_count = event[6]

                values = [
                    event_id,
                    event_date,
                    event_type,
                    description,
                    processed_count,
                    success_count,
                    error_count,
                ]

                for column, value in enumerate(values):

                    self.table.setItem(
                        row,
                        column,
                        QTableWidgetItem(
                            str(value)
                        )
                    )

            self.table.resizeColumnsToContents()

            self.table.setColumnWidth(0, 60)
            self.table.setColumnWidth(1, 150)
            self.table.setColumnWidth(2, 180)
            self.table.setColumnWidth(3, 400)
            self.table.setColumnWidth(4, 90)
            self.table.setColumnWidth(5, 90)
            self.table.setColumnWidth(6, 90)

        except Exception as error:

            QMessageBox.critical(
                self,
                "Error",
                (
                    "No se pudo cargar el historial:"
                    f"\n\n{error}"
                )
            )

    def clear_history(self):

        if self.table.rowCount() == 0:

            QMessageBox.information(
                self,
                "Historial",
                "El historial ya está vacío."
            )

            return

        respuesta = QMessageBox.question(
            self,
            "Limpiar historial",
            (
                "¿Estás seguro de que quieres "
                "eliminar todo el historial?\n\n"
                "Esta acción no se puede deshacer."
            ),
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if respuesta != QMessageBox.StandardButton.Yes:
            return

        try:

            deleted = self.service.clear()

            self.load_history()

            QMessageBox.information(
                self,
                "Historial",
                (
                    f"Se han eliminado {deleted} "
                    "registro(s) del historial."
                )
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Error",
                (
                    "No se pudo limpiar el historial:"
                    f"\n\n{error}"
                )
            )
