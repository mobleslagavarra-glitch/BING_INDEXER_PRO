import pytest

from services.settings_service import SettingsService


class FakeRepository:

    def __init__(self, settings=None):
        self.settings = dict(settings or {})
        self.set_calls = []
        self.delete_calls = []

    def get(self, key, default=None):
        return self.settings.get(key, default)

    def set(self, key, value):
        self.set_calls.append((key, value))
        self.settings[key] = str(value)
        return True

    def get_all(self):
        return list(self.settings.items())

    def delete(self, key):
        self.delete_calls.append(key)

        if key in self.settings:
            del self.settings[key]
            return True

        return False


def create_service(monkeypatch, settings=None):

    repository = FakeRepository(settings)

    monkeypatch.setattr(
        "services.settings_service.SettingsRepository",
        lambda: repository
    )

    return SettingsService(), repository


def test_get_existing_setting(monkeypatch):

    service, _ = create_service(
        monkeypatch,
        {"indexnow_auto": "1"}
    )

    assert service.get("indexnow_auto") == "1"


def test_get_uses_service_default(monkeypatch):

    service, _ = create_service(monkeypatch)

    assert service.get("indexnow_auto") == "0"
    assert service.get("indexnow_retries") == "3"
    assert service.get("indexnow_interval") == "1"


def test_get_explicit_default(monkeypatch):

    service, _ = create_service(monkeypatch)

    assert service.get(
        "clave_inexistente",
        "valor_personalizado"
    ) == "valor_personalizado"


def test_get_unknown_setting_without_default(monkeypatch):

    service, _ = create_service(monkeypatch)

    assert service.get("clave_inexistente") is None


def test_get_requires_key(monkeypatch):

    service, _ = create_service(monkeypatch)

    with pytest.raises(
        ValueError,
        match="La clave de configuración es obligatoria"
    ):
        service.get("")


def test_get_none_key_fails(monkeypatch):

    service, _ = create_service(monkeypatch)

    with pytest.raises(
        ValueError,
        match="La clave de configuración es obligatoria"
    ):
        service.get(None)


def test_set_setting(monkeypatch):

    service, repository = create_service(monkeypatch)

    result = service.set(
        "indexnow_auto",
        "1"
    )

    assert result is True
    assert repository.settings["indexnow_auto"] == "1"
    assert repository.set_calls == [
        ("indexnow_auto", "1")
    ]


def test_set_requires_key(monkeypatch):

    service, _ = create_service(monkeypatch)

    with pytest.raises(
        ValueError,
        match="La clave de configuración es obligatoria"
    ):
        service.set("", "1")


def test_get_all(monkeypatch):

    service, _ = create_service(
        monkeypatch,
        {
            "indexnow_auto": "1",
            "indexnow_interval": "5"
        }
    )

    result = service.get_all()

    assert ("indexnow_auto", "1") in result
    assert ("indexnow_interval", "5") in result


def test_delete_setting(monkeypatch):

    service, repository = create_service(
        monkeypatch,
        {"indexnow_auto": "1"}
    )

    result = service.delete("indexnow_auto")

    assert result is True
    assert "indexnow_auto" not in repository.settings
    assert repository.delete_calls == ["indexnow_auto"]


def test_delete_missing_setting(monkeypatch):

    service, _ = create_service(monkeypatch)

    assert service.delete("no_existe") is False


def test_delete_requires_key(monkeypatch):

    service, _ = create_service(monkeypatch)

    with pytest.raises(
        ValueError,
        match="La clave de configuración es obligatoria"
    ):
        service.delete("")


def test_initialize_defaults_creates_missing_settings(monkeypatch):

    service, repository = create_service(monkeypatch)

    service.initialize_defaults()

    assert repository.settings == SettingsService.DEFAULTS

    assert repository.set_calls == [
        ("indexnow_auto", "0"),
        ("indexnow_retries", "3"),
        ("indexnow_interval", "1")
    ]


def test_initialize_defaults_does_not_overwrite_existing(
    monkeypatch
):

    service, repository = create_service(
        monkeypatch,
        {
            "indexnow_auto": "1"
        }
    )

    service.initialize_defaults()

    assert repository.settings["indexnow_auto"] == "1"

    assert repository.settings["indexnow_retries"] == "3"
    assert repository.settings["indexnow_interval"] == "1"

    assert repository.set_calls == [
        ("indexnow_retries", "3"),
        ("indexnow_interval", "1")
    ]


def test_initialize_defaults_with_all_settings_does_nothing(
    monkeypatch
):

    existing = dict(SettingsService.DEFAULTS)

    service, repository = create_service(
        monkeypatch,
        existing
    )

    service.initialize_defaults()

    assert repository.settings == existing
    assert repository.set_calls == []
