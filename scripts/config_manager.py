"""
======================================================
BING INDEXER PRO 2026
Config Manager
======================================================
Gestiona toda la configuración del programa.
"""

import json
from pathlib import Path


class ConfigManager:

    def __init__(self, config_path="config/config.json"):

        self.config_path = Path(config_path)

        self.config = {}

        self.load()

    def load(self):

        if not self.config_path.exists():

            raise FileNotFoundError(
                f"No existe {self.config_path}"
            )

        with open(self.config_path,
                  "r",
                  encoding="utf-8") as file:

            self.config = json.load(file)

    def save(self):

        with open(self.config_path,
                  "w",
                  encoding="utf-8") as file:

            json.dump(
                self.config,
                file,
                indent=4,
                ensure_ascii=False
            )

    def get(self, key, default=None):

        return self.config.get(key, default)

    def set(self, key, value):

        self.config[key] = value

        self.save()