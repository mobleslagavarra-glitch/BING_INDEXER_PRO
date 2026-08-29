from models.url import UrlRecord
from models.domain import Domain
from services.url_service import UrlService


class FakeUrlRepository:

    def __init__(self):
        self.urls = []
        self.next_id = 1

    def get_all(self):
        return list(self.urls)

    def get_by_id(self, url_id):
        for url in self.urls:
            if url.id == url_id:
                return url

        return None

    def create(self, url_record):
        url_record.id = self.next_id
        self.next_id += 1
        self.urls.append(url_record)
        return url_record

    def update(self, url_record):
        for index, item in enumerate(self.urls):
            if item.id == url_record.id:
                self.urls[index] = url_record
                return True

        return False

    def delete(self, url_id):
        original_length = len(self.urls)

        self.urls = [
            url
            for url in self.urls
            if url.id != url_id
        ]

        return len(self.urls) < original_length


class FakeDomainRepository:

    def __init__(self):
        self.domains = [
            Domain(
                id=1,
                domain="example.com",
                api_key="TEST_KEY",
                enabled=True
            ),
            Domain(
                id=2,
                domain="example.org",
                api_key="TEST_KEY",
                enabled=True
            )
        ]

    def get_by_id(self, domain_id):
        for domain in self.domains:
            if domain.id == domain_id:
                return domain

        return None


def create_service(monkeypatch):

    url_repository = FakeUrlRepository()
    domain_repository = FakeDomainRepository()

    monkeypatch.setattr(
        "services.url_service.UrlRepository",
        lambda: url_repository
    )

    monkeypatch.setattr(
        "services.url_service.DomainRepository",
        lambda: domain_repository
    )

    return (
        UrlService(),
        url_repository,
        domain_repository
    )


def test_add_url_creates_pending_url(monkeypatch):

    service, repository, _ = create_service(monkeypatch)

    result = service.add_url(
        1,
        "  https://example.com/prueba  "
    )

    assert result.id == 1
    assert result.domain_id == 1
    assert result.url == "https://example.com/prueba"
    assert result.status == "PENDIENTE"
    assert result.response_code is None
    assert result.response_message == ""
    assert len(repository.urls) == 1


def test_add_empty_url_fails(monkeypatch):

    service, _, _ = create_service(monkeypatch)

    try:
        service.add_url(1, "   ")
        assert False
    except ValueError as error:
        assert str(error) == "La URL no puede estar vacía"


def test_add_url_with_unknown_domain_fails(monkeypatch):

    service, _, _ = create_service(monkeypatch)

    try:
        service.add_url(
            999,
            "https://example.com/prueba"
        )
        assert False
    except ValueError as error:
        assert str(error) == "El dominio no existe"


def test_add_url_from_different_domain_fails(monkeypatch):

    service, _, _ = create_service(monkeypatch)

    try:
        service.add_url(
            1,
            "https://example.org/prueba"
        )
        assert False
    except ValueError as error:
        assert "no pertenece al dominio seleccionado" in str(error)


def test_duplicate_url_fails(monkeypatch):

    service, _, _ = create_service(monkeypatch)

    service.add_url(
        1,
        "https://example.com/prueba"
    )

    try:
        service.add_url(
            1,
            "https://EXAMPLE.COM/prueba"
        )
        assert False
    except ValueError as error:
        assert "ya existe" in str(error)


def test_update_url(monkeypatch):

    service, repository, _ = create_service(monkeypatch)

    url = service.add_url(
        1,
        "https://example.com/antigua"
    )

    url.url = "  https://example.com/nueva  "

    result = service.update_url(url)

    assert result is True
    assert url.url == "https://example.com/nueva"


def test_delete_url(monkeypatch):

    service, _, _ = create_service(monkeypatch)

    url = service.add_url(
        1,
        "https://example.com/prueba"
    )

    assert service.delete_url(url.id) is True
    assert service.get_url(url.id) is None

def test_update_url_resets_indexing_status(monkeypatch):

    service, repository, _ = create_service(monkeypatch)

    url = service.add_url(
        1,
        "https://example.com/antigua"
    )

    url.status = "ENVIADA"
    url.response_code = 202
    url.response_message = "Aceptado"

    url.url = "https://example.com/nueva"

    result = service.update_url(url)

    assert result is True
    assert url.url == "https://example.com/nueva"
    assert url.status == "PENDIENTE"
    assert url.response_code is None
    assert url.response_message == ""
