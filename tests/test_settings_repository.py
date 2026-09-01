import sqlite3

from repositories.settings_repository import SettingsRepository


def create_settings_database(path):
    conn = sqlite3.connect(path)

    try:
        conn.execute("""
            CREATE TABLE settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                value TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()

    finally:
        conn.close()


def create_repository(monkeypatch, tmp_path):
    db_file = str(tmp_path / "settings.db")

    monkeypatch.setattr(
        "repositories.settings_repository.DB_FILE",
        db_file
    )

    create_settings_database(db_file)

    return SettingsRepository()


def test_get_returns_default_when_key_does_not_exist(
    monkeypatch,
    tmp_path
):
    repository = create_repository(
        monkeypatch,
        tmp_path
    )

    assert repository.get(
        "clave_inexistente",
        "valor_defecto"
    ) == "valor_defecto"


def test_set_and_get_setting(
    monkeypatch,
    tmp_path
):
    repository = create_repository(
        monkeypatch,
        tmp_path
    )

    assert repository.set(
        "indexnow_auto",
        "1"
    ) is True

    assert repository.get(
        "indexnow_auto"
    ) == "1"


def test_get_all_returns_settings(
    monkeypatch,
    tmp_path
):
    repository = create_repository(
        monkeypatch,
        tmp_path
    )

    repository.set(
        "indexnow_auto",
        "1"
    )

    repository.set(
        "indexnow_interval",
        "5"
    )

    settings = repository.get_all()

    assert ("indexnow_auto", "1") in settings
    assert ("indexnow_interval", "5") in settings


def test_delete_setting(
    monkeypatch,
    tmp_path
):
    repository = create_repository(
        monkeypatch,
        tmp_path
    )

    repository.set(
        "indexnow_auto",
        "1"
    )

    assert repository.delete(
        "indexnow_auto"
    ) is True

    assert repository.get(
        "indexnow_auto"
    ) is None


def test_delete_missing_setting(
    monkeypatch,
    tmp_path
):
    repository = create_repository(
        monkeypatch,
        tmp_path
    )

    assert repository.delete(
        "no_existe"
    ) is False
