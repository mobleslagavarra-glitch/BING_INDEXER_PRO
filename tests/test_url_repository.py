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

def test_get_all_empty_returns_empty_list(
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

    assert repository.get_all() == []


def test_get_by_id_converts_null_response_message_to_empty_string(
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

    conn = repository.get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO urls (
                domain_id,
                url,
                status,
                response_code,
                response_message
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                1,
                "https://example.com/null-message",
                "PENDIENTE",
                None,
                None
            )
        )

        conn.commit()

        url_id = cursor.lastrowid

    finally:
        conn.close()

    result = repository.get_by_id(url_id)

    assert result is not None
    assert result.response_message == ""


def test_create_many_preserves_response_data(
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

    records = [
        (
            1,
            "https://example.com/uno",
            "ENVIADA",
            200,
            "OK"
        ),
        (
            1,
            "https://example.com/dos",
            "ERROR",
            500,
            "Error servidor"
        ),
    ]

    created = repository.create_many(records)

    assert created == 2

    results = repository.get_all()

    assert len(results) == 2

    by_url = {
        record.url: record
        for record in results
    }

    assert by_url[
        "https://example.com/uno"
    ].status == "ENVIADA"

    assert by_url[
        "https://example.com/uno"
    ].response_code == 200

    assert by_url[
        "https://example.com/uno"
    ].response_message == "OK"

    assert by_url[
        "https://example.com/dos"
    ].status == "ERROR"

    assert by_url[
        "https://example.com/dos"
    ].response_code == 500

    assert by_url[
        "https://example.com/dos"
    ].response_message == "Error servidor"
