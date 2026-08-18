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

    def __init__(self):
        super().__init__()

        self.service = HistoryService()

        layout = QVBoxLayout()

        titulo = QLabel("Historial")
        layout.addWidget(titulo)

        self.table = QTableWidget()
        self.table.setColumnCount(4)

        self.table.setHorizontalHeaderLabels([
            "ID",
            "Fecha / Hora",
            "Tipo",
            "Descripción",
        ])

        self.table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

        self.table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )

        self.table.setAlternatingRowColors(True)

        layout.addWidget(self.table)

        botones = QHBoxLayout()

        self.btn_refresh = QPushButton("Actualizar")

        botones.addStretch()
        botones.addWidget(self.btn_refresh)

        layout.addLayout(botones)

        self.setLayout(layout)

        self.btn_refresh.clicked.connect(
            self.load_history
        )

        self.load_history()

    def load_history(self):

        try:
            history = self.service.get_all()

            self.table.setRowCount(len(history))

            for row, event in enumerate(history):

                event_id = event[0]
                event_date = event[1]
                event_type = event[2]
                description = event[3]

                self.table.setItem(
                    row,
                    0,
                    QTableWidgetItem(str(event_id))
                )

                self.table.setItem(
                    row,
                    1,
                    QTableWidgetItem(str(event_date))
                )

                self.table.setItem(
                    row,
                    2,
                    QTableWidgetItem(str(event_type))
                )

                self.table.setItem(
                    row,
                    3,
                    QTableWidgetItem(str(description))
                )

            self.table.resizeColumnsToContents()

            self.table.setColumnWidth(3, 600)

        except Exception as error:

            QMessageBox.critical(
                self,
                "Error",
                f"No se pudo cargar el historial:\n\n{error}"
            )