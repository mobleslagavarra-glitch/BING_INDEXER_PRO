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
from gui.dialogs.domain_dialog import DomainDialog


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
        self.btn_edit = QPushButton("✏️ Editar")
        self.btn_delete = QPushButton("🗑️ Eliminar")
        self.btn_refresh = QPushButton("🔄 Actualizar")

        botones.addWidget(self.btn_add)
        botones.addWidget(self.btn_edit)
        botones.addWidget(self.btn_delete)

        botones.addStretch()

        botones.addWidget(self.btn_refresh)

        layout.addLayout(botones)

        self.setLayout(layout)

        self.btn_add.clicked.connect(self.add_domain)
        self.btn_edit.clicked.connect(self.edit_domain)
        self.btn_delete.clicked.connect(self.delete_domain)
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

                estado = (
                    "Activo"
                    if domain.enabled
                    else "Desactivado"
                )

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

    def add_domain(self):

        dialog = DomainDialog(self)

        if dialog.exec() != DomainDialog.DialogCode.Accepted:
            return

        data = dialog.get_data()

        try:

            self.service.add_domain(
                data["domain"],
                data["api_key"],
                data["enabled"],
            )

            self.load_domains()

            QMessageBox.information(
                self,
                "Dominio añadido",
                "El dominio se ha añadido correctamente."
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Error",
                f"No se pudo añadir el dominio:\n\n{error}"
            )

    def edit_domain(self):

        row = self.table.currentRow()

        if row < 0:

            QMessageBox.warning(
                self,
                "Editar dominio",
                "Selecciona un dominio de la lista."
            )

            return

        try:

            domain_id = int(
                self.table.item(row, 0).text()
            )

            domain = self.service.get_domain(domain_id)

            if domain is None:

                QMessageBox.warning(
                    self,
                    "Editar dominio",
                    "El dominio seleccionado no existe."
                )

                self.load_domains()
                return

            dialog = DomainDialog(self)

            dialog.setWindowTitle(
                "Editar dominio"
            )

            dialog.domain_edit.setText(
                domain.domain
            )

            dialog.api_key_edit.setText(
                domain.api_key
            )

            dialog.enabled_check.setChecked(
                domain.enabled
            )

            if dialog.exec() != DomainDialog.DialogCode.Accepted:
                return

            data = dialog.get_data()

            domain.domain = data["domain"]
            domain.api_key = data["api_key"]
            domain.enabled = data["enabled"]

            self.service.update_domain(domain)

            self.load_domains()

            QMessageBox.information(
                self,
                "Dominio actualizado",
                "El dominio se ha actualizado correctamente."
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Error",
                f"No se pudo actualizar el dominio:\n\n{error}"
            )

    def delete_domain(self):

        row = self.table.currentRow()

        if row < 0:

            QMessageBox.warning(
                self,
                "Eliminar dominio",
                "Selecciona un dominio de la lista."
            )

            return

        try:

            domain_id = int(
                self.table.item(row, 0).text()
            )

            domain_name = self.table.item(
                row,
                1
            ).text()

            answer = QMessageBox.question(
                self,
                "Eliminar dominio",
                f"¿Seguro que quieres eliminar el dominio\n\n"
                f"{domain_name}?",
                QMessageBox.StandardButton.Yes
                | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )

            if answer != QMessageBox.StandardButton.Yes:
                return

            self.service.delete_domain(domain_id)

            self.load_domains()

            QMessageBox.information(
                self,
                "Dominio eliminado",
                "El dominio se ha eliminado correctamente."
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Error",
                f"No se pudo eliminar el dominio:\n\n{error}"
            )