import pytest
import sqlite3

from models.domain import Domain
from repositories.domain_repository import DomainRepository


def create_test_database(tmp_path, monkeypatch):
    db_file = tmp_path / "test_bing_indexer.db"

    connection = sqlite3.connect(db_file)

    connection.execute("""
        CREATE TABLE domains (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            domain TEXT UNIQUE NOT NULL,
            api_key TEXT,
            enabled INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()
    connection.close()

    monkeypatch.setattr(
        "repositories.domain_repository.DB_FILE",
        db_file
    )

    return DomainRepository()


def test_create_and_get_domain(tmp_path, monkeypatch):
    repository = create_test_database(tmp_path, monkeypatch)

    domain = Domain(
        domain="example.com",
        api_key="TEST_KEY",
        enabled=True
    )

    created = repository.create(domain)

    assert created.id is not None

    result = repository.get_by_id(created.id)

    assert result is not None
    assert result.domain == "example.com"
    assert result.api_key == "TEST_KEY"
    assert result.enabled is True


def test_get_all_domains(tmp_path, monkeypatch):
    repository = create_test_database(tmp_path, monkeypatch)

    repository.create(
        Domain(
            domain="example.com",
            api_key="KEY1",
            enabled=True
        )
    )

    repository.create(
        Domain(
            domain="example.org",
            api_key="KEY2",
            enabled=False
        )
    )

    domains = repository.get_all()

    assert len(domains) == 2
    assert domains[0].domain == "example.com"
    assert domains[1].domain == "example.org"


def test_update_domain(tmp_path, monkeypatch):
    repository = create_test_database(tmp_path, monkeypatch)

    domain = repository.create(
        Domain(
            domain="example.com",
            api_key="OLD_KEY",
            enabled=True
        )
    )

    domain.domain = "example.org"
    domain.api_key = "NEW_KEY"
    domain.enabled = False

    result = repository.update(domain)

    assert result is True

    updated = repository.get_by_id(domain.id)

    assert updated.domain == "example.org"
    assert updated.api_key == "NEW_KEY"
    assert updated.enabled is False


def test_delete_domain(tmp_path, monkeypatch):
    repository = create_test_database(tmp_path, monkeypatch)

    domain = repository.create(
        Domain(
            domain="example.com",
            api_key="TEST_KEY",
            enabled=True
        )
    )

    result = repository.delete(domain.id)

    assert result is True
    assert repository.get_by_id(domain.id) is None


def test_get_by_id_returns_none_for_missing_domain(
    tmp_path,
    monkeypatch
):
    repository = create_test_database(
        tmp_path,
        monkeypatch
    )

    assert repository.get_by_id(999) is None


def test_update_domain_without_id_fails():
    repository = DomainRepository()

    domain = Domain(
        id=None,
        domain="example.com",
        api_key="KEY",
        enabled=True
    )

    with pytest.raises(
        ValueError,
        match="sin ID"
    ):
        repository.update(domain)


def test_update_missing_domain_returns_false(
    tmp_path,
    monkeypatch
):
    repository = create_test_database(
        tmp_path,
        monkeypatch
    )

    domain = Domain(
        id=999,
        domain="example.com",
        api_key="KEY",
        enabled=True
    )

    assert repository.update(domain) is False


def test_delete_missing_domain_returns_false(
    tmp_path,
    monkeypatch
):
    repository = create_test_database(
        tmp_path,
        monkeypatch
    )

    assert repository.delete(999) is False
