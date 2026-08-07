"""
Lectura de archivos
"""

from pathlib import Path


class FileManager:

    @staticmethod
    def read_txt(file):

        file = Path(file)

        if not file.exists():

            return []

        with open(file,
                  encoding="utf-8") as f:

            return [

                line.strip()

                for line in f

                if line.strip()

            ]