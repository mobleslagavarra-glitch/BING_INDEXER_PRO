from repositories.settings_repository import SettingsRepository


class SettingsService:

    DEFAULTS = {
        "indexnow_auto": "0",
        "indexnow_retries": "3",
        "indexnow_interval": "1",
    }

    def __init__(self):
        self.repository = SettingsRepository()

    def get(self, key, default=None):
        if not key:
            raise ValueError("La clave de configuración es obligatoria")

        if default is None:
            default = self.DEFAULTS.get(key)

        return self.repository.get(key, default)

    def set(self, key, value):
        if not key:
            raise ValueError("La clave de configuración es obligatoria")

        return self.repository.set(key, value)

    def get_all(self):
        return self.repository.get_all()

    def delete(self, key):
        if not key:
            raise ValueError("La clave de configuración es obligatoria")

        return self.repository.delete(key)

    def initialize_defaults(self):
        for key, value in self.DEFAULTS.items():

            existing = self.repository.get(key)

            if existing is None:
                self.repository.set(key, value)
