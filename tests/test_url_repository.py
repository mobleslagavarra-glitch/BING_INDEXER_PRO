import sqlite3

import pytest

from core.database import initialize_database
from models.url import UrlRecord
from repositories.url_repository import UrlRepository


def test_create_and_get_by_id(tmp_path, monkeypatch):

    db_file = tmp_path / "test.db"

    monkeypatch.setattr(
        "repositories.url_repository.DB_FILE",
        db_file
    )

    monkeypatch.setattr(
        "core.database.DB_FILE",
        db_file
    )

    initialize_database()

    repository = UrlRepository()

    record = UrlRecord(
        id=None,
        domain_id=1,
        url="https://example.com/prueba",
        status="PENDIENTE",
        response_code=None,
        response_message=""
    )

    created = repository.create(record)

    assert created.id is not None

    result = repository.get_by_id(
        created.id
    )

    assert result is not None
    assert result.id == created.id
    assert result.domain_id == 1
    assert result.url == "https://example.com/prueba"
    assert result.status == "PENDIENTE"


def test_get_by_id_returns_none_for_missing_id(
    tmp_path,
    monkeypatch
):

    db_file = tmp_path / "test.db"

    monkeypatch.setattr(
        "repositories.url_repository.DB_FILE",
        db_file
    )

    monkeypatch.setattr(
        "core.database.DB_FILE",
        db_file
    )

    initialize_database()

    repository = UrlRepository()

    assert repository.get_by_id(999) is None


def test_get_all_returns_urls_ordered_by_url(
    tmp_path,
    monkeypatch
):

    db_file = tmp_path / "test.db"

    monkeypatch.setattr(
        "repositories.url_repository.DB_FILE",
        db_file
    )

    monkeypatch.setattr(
        "core.database.DB_FILE",
        db_file
    )

    initialize_database()

    repository = UrlRepository()

    repository.create(
        UrlRecord(
            id=None,
            domain_id=1,
            url="https://example.com/z",
            status="PENDIENTE",
            response_code=None,
            response_message=""
        )
    )

    repository.create(
        UrlRecord(
            id=None,
            domain_id=1,
            url="https://example.com/a",
            status="ENVIADA",
            response_code=202,
            response_message="Aceptado"
        )
    )

    results = repository.get_all()

    assert len(results) == 2
    assert results[0].url == "https://example.com/a"
    assert results[1].url == "https://example.com/z"


def test_update_url(tmp_path, monkeypatch):

    db_file = tmp_path / "test.db"

    monkeypatch.setattr(
        "repositories.url_repository.DB_FILE",
        db_file
    )

    monkeypatch.setattr(
        "core.database.DB_FILE",
        db_file
    )

    initialize_database()

    repository = UrlRepository()

    record = repository.create(
        UrlRecord(
            id=None,
            domain_id=1,
            url="https://example.com/prueba",
            status="PENDIENTE",
            response_code=None,
            response_message=""
        )
    )

    record.status = "ENVIADA"
    record.response_code = 202
    record.response_message = "Aceptado"

    result = repository.update(record)

    assert result is True

    updated = repository.get_by_id(record.id)

    assert updated.status == "ENVIADA"
    assert updated.response_code == 202
    assert updated.response_message == "Aceptado"


def test_update_without_id_fails():

    repository = UrlRepository()

    record = UrlRecord(
        id=None,
        domain_id=1,
        url="https://example.com/prueba",
        status="PENDIENTE"
    )

    with pytest.raises(
        ValueError,
        match="sin ID"
    ):
        repository.update(record)


def test_update_missing_url_returns_false(
    tmp_path,
    monkeypatch
):

    db_file = tmp_path / "test.db"

    monkeypatch.setattr(
        "repositories.url_repository.DB_FILE",
        db_file
    )

    monkeypatch.setattr(
        "core.database.DB_FILE",
        db_file
    )

    initialize_database()

    repository = UrlRepository()

    record = UrlRecord(
        id=999,
        domain_id=1,
        url="https://example.com/no-existe",
        status="PENDIENTE"
    )

    assert repository.update(record) is False


def test_create_many(tmp_path, monkeypatch):

    db_file = tmp_path / "test.db"

    monkeypatch.setattr(
        "repositories.url_repository.DB_FILE",
        db_file
    )

    monkeypatch.setattr(
        "core.database.DB_FILE",
        db_file
    )

    initialize_database()

    repository = UrlRepository()

    records = [
        (
            1,
            "https://example.com/uno",
            "PENDIENTE",
            None,
            ""
        ),
        (
            1,
            "https://example.com/dos",
            "PENDIENTE",
            None,
            ""
        ),
    ]

    created = repository.create_many(records)

    assert created == 2

    results = repository.get_all()

    assert len(results) == 2


def test_create_many_empty_returns_zero():

    repository = UrlRepository()

    assert repository.create_many([]) == 0


def test_delete_url(tmp_path, monkeypatch):

    db_file = tmp_path / "test.db"

    monkeypatch.setattr(
        "repositories.url_repository.DB_FILE",
        db_file
    )

    monkeypatch.setattr(
        "core.database.DB_FILE",
        db_file
    )

    initialize_database()

    repository = UrlRepository()

    record = repository.create(
        UrlRecord(
            id=None,
            domain_id=1,
            url="https://example.com/prueba",
            status="PENDIENTE"
        )
    )

    assert repository.delete(record.id) is True
    assert repository.get_by_id(record.id) is None


def test_delete_missing_url_returns_false(
    tmp_path,
    monkeypatch
):

    db_file = tmp_path / "test.db"

    monkeypatch.setattr(
        "repositories.url_repository.DB_FILE",
        db_file
    )

    monkeypatch.setattr(
        "core.database.DB_FILE",
        db_file
    )

    initialize_database()

    repository = UrlRepository()

    assert repository.delete(999) is False
