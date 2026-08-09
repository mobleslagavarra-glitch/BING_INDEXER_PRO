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

from services.domain_service import DomainService


class DomainsPage(QWidget):

    def __init__(self):
        super().__init__()

        self.service = DomainService()

        layout = QVBoxLayout()

        titulo = QLabel("Dominios")

        layout.addWidget(titulo)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([
            "ID",
            "Dominio",
            "API Key",
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

        self.btn_add = QPushButton("➕ Añadir")
        self.btn_edit = QPushButton("✏ Editar")
        self.btn_delete = QPushButton("🗑 Eliminar")
        self.btn_refresh = QPushButton("🔄 Actualizar")

        botones.addWidget(self.btn_add)
        botones.addWidget(self.btn_edit)
        botones.addWidget(self.btn_delete)

        botones.addStretch()

        botones.addWidget(self.btn_refresh)

        layout.addLayout(botones)

        self.setLayout(layout)

        self.btn_refresh.clicked.connect(self.load_domains)

        self.load_domains()

    def load_domains(self):
        try:
            domains = self.service.get_domains()

            self.table.setRowCount(len(domains))

            for row, domain in enumerate(domains):
                self.table.setItem(
                    row,
                    0,
                    QTableWidgetItem(str(domain.id))
                )

                self.table.setItem(
                    row,
                    1,
                    QTableWidgetItem(domain.domain)
                )

                self.table.setItem(
                    row,
                    2,
                    QTableWidgetItem(domain.api_key)
                )

                estado = "Activo" if domain.enabled else "Desactivado"

                self.table.setItem(
                    row,
                    3,
                    QTableWidgetItem(estado)
                )

            self.table.resizeColumnsToContents()

        except Exception as error:
            QMessageBox.critical(
                self,
                "Error",
                f"No se pudieron cargar los dominios:\n\n{error}"
            )