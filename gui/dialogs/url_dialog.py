from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QLineEdit,
    QComboBox,
    QDialogButtonBox,
)


class UrlDialog(QDialog):

    def __init__(self, domains, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Añadir URL")
        self.setMinimumWidth(500)

        layout = QFormLayout(self)

        self.domain_combo = QComboBox()

        for domain in domains:
            self.domain_combo.addItem(
                domain.domain,
                domain.id
            )

        self.url_edit = QLineEdit()
        self.url_edit.setPlaceholderText(
            "https://ejemplo.com/pagina"
        )

        layout.addRow(
            "Dominio:",
            self.domain_combo
        )

        layout.addRow(
            "URL:",
            self.url_edit
        )

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )

        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout.addRow(buttons)

    def get_data(self):
        return {
            "domain_id": self.domain_combo.currentData(),
            "url": self.url_edit.text(),
        }