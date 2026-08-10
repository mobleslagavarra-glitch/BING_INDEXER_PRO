from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QLineEdit,
    QCheckBox,
    QDialogButtonBox,
)


class DomainDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Añadir dominio")
        self.setMinimumWidth(400)

        layout = QFormLayout(self)

        self.domain_edit = QLineEdit()
        self.domain_edit.setPlaceholderText("ejemplo.com")

        self.api_key_edit = QLineEdit()
        self.api_key_edit.setPlaceholderText("API Key de Bing")

        self.enabled_check = QCheckBox()
        self.enabled_check.setChecked(True)

        layout.addRow("Dominio:", self.domain_edit)
        layout.addRow("API Key:", self.api_key_edit)
        layout.addRow("Estado:", self.enabled_check)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )

        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout.addRow(buttons)

    def get_data(self):
        return {
            "domain": self.domain_edit.text(),
            "api_key": self.api_key_edit.text(),
            "enabled": self.enabled_check.isChecked(),
        }