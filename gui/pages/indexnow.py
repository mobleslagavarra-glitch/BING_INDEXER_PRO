from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
)


class IndexNowPage(QWidget):

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        title = QLabel("IndexNow")

        description = QLabel(
            "Desde aquí podrás enviar URLs a IndexNow."
        )

        layout.addWidget(title)
        layout.addWidget(description)
        layout.addStretch()

        self.setLayout(layout)