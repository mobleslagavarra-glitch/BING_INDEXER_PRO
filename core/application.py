from pathlib import Path

from PySide6.QtWidgets import QApplication

from core.paths import FOLDERS
from core.database import initialize_database
from core.logger import logger

from gui.main_window import MainWindow


class Application:

    def __init__(self):

        self.create_folders()

        initialize_database()

        logger.info("Base de datos inicializada")

        self.qt = QApplication([])

        self.window = MainWindow()

    def create_folders(self):

        for folder in FOLDERS:

            Path(folder).mkdir(
                parents=True,
                exist_ok=True
            )

    def run(self):

        self.window.show()

        self.qt.exec()