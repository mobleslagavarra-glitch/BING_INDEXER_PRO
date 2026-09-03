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


def test_add_url_without_domain_id_fails(monkeypatch):

    service, _, _ = create_service(monkeypatch)

    try:
        service.add_url(None, "https://example.com/prueba")
        assert False
    except ValueError as error:
        assert str(error) == "El ID del dominio es obligatorio"


def test_add_empty_url_fails(monkeypatch):

    service, _, _ = create_service(monkeypatch)

    try:
        service.add_url(1, "   ")
        assert False
    except ValueError as error:
        assert str(error) == "La URL no puede estar vacía"


def test_add_none_url_fails(monkeypatch):

    service, _, _ = create_service(monkeypatch)

    try:
        service.add_url(1, None)
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


def test_duplicate_url_detection_ignores_case(monkeypatch):

    service, _, _ = create_service(monkeypatch)

    service.add_url(
        1,
        "https://example.com/Prueba"
    )

    try:
        service.add_url(
            1,
            "HTTPS://EXAMPLE.COM/PRUEBA"
        )
        assert False
    except ValueError as error:
        assert "ya existe" in str(error)


def test_add_url_accepts_http(monkeypatch):

    service, _, _ = create_service(monkeypatch)

    result = service.add_url(
        1,
        "http://example.com/prueba"
    )

    assert result.url == "http://example.com/prueba"


def test_normalize_markdown_url():

    result = UrlService._normalize_url(
        "[Página de prueba](https://example.com/prueba)"
    )

    assert result == "Página de prueba"


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


def test_update_url_resets_indexing_status(monkeypatch):

    service, _, _ = create_service(monkeypatch)

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


def test_update_url_without_id_fails(monkeypatch):

    service, _, _ = create_service(monkeypatch)

    url = UrlRecord(
        id=None,
        domain_id=1,
        url="https://example.com/prueba",
        status="PENDIENTE"
    )

    try:
        service.update_url(url)
        assert False
    except ValueError as error:
        assert str(error) == "La URL debe tener un ID"


def test_update_url_invalid_type_fails(monkeypatch):

    service, _, _ = create_service(monkeypatch)

    try:
        service.update_url("https://example.com/prueba")
        assert False
    except TypeError as error:
        assert str(error) == "Se esperaba un objeto UrlRecord"


def test_update_url_with_unknown_id_fails(monkeypatch):

    service, _, _ = create_service(monkeypatch)

    url = UrlRecord(
        id=999,
        domain_id=1,
        url="https://example.com/prueba",
        status="PENDIENTE"
    )

    try:
        service.update_url(url)
        assert False
    except ValueError as error:
        assert str(error) == "La URL no existe"


def test_update_url_with_unknown_domain_fails(monkeypatch):

    service, _, _ = create_service(monkeypatch)

    url = service.add_url(
        1,
        "https://example.com/prueba"
    )

    url.domain_id = 999

    try:
        service.update_url(url)
        assert False
    except ValueError as error:
        assert str(error) == "El dominio no existe"


def test_update_url_empty_url_fails(monkeypatch):

    service, _, _ = create_service(monkeypatch)

    url = service.add_url(
        1,
        "https://example.com/prueba"
    )

    url.url = "   "

    try:
        service.update_url(url)
        assert False
    except ValueError as error:
        assert str(error) == "La URL no puede estar vacía"


def test_update_url_different_domain_fails(monkeypatch):

    service, _, _ = create_service(monkeypatch)

    url = service.add_url(
        1,
        "https://example.com/prueba"
    )

    url.url = "https://example.org/otra"

    try:
        service.update_url(url)
        assert False
    except ValueError as error:
        assert "no pertenece al dominio seleccionado" in str(error)


def test_update_url_duplicate_fails(monkeypatch):

    service, _, _ = create_service(monkeypatch)

    first = service.add_url(
        1,
        "https://example.com/uno"
    )

    second = service.add_url(
        1,
        "https://example.com/dos"
    )

    second.url = first.url

    try:
        service.update_url(second)
        assert False
    except ValueError as error:
        assert "ya existe" in str(error)


def test_update_url_same_url_is_allowed(monkeypatch):

    service, _, _ = create_service(monkeypatch)

    url = service.add_url(
        1,
        "https://example.com/prueba"
    )

    result = service.update_url(url)

    assert result is True
    assert url.url == "https://example.com/prueba"


def test_delete_url(monkeypatch):

    service, _, _ = create_service(monkeypatch)

    url = service.add_url(
        1,
        "https://example.com/prueba"
    )

    assert service.delete_url(url.id) is True
    assert service.get_url(url.id) is None


def test_delete_unknown_url_returns_false(monkeypatch):

    service, _, _ = create_service(monkeypatch)

    assert service.delete_url(999) is False


def test_delete_url_without_id_fails(monkeypatch):

    service, _, _ = create_service(monkeypatch)

    try:
        service.delete_url(None)
        assert False
    except ValueError as error:
        assert str(error) == "El ID de la URL es obligatorio"


def test_get_urls(monkeypatch):

    service, _, _ = create_service(monkeypatch)

    first = service.add_url(
        1,
        "https://example.com/uno"
    )

    second = service.add_url(
        1,
        "https://example.com/dos"
    )

    urls = service.get_urls()

    assert len(urls) == 2
    assert urls[0] == first
    assert urls[1] == second


def test_get_urls_returns_empty_list(monkeypatch):

    service, _, _ = create_service(monkeypatch)

    assert service.get_urls() == []


def test_get_url(monkeypatch):

    service, _, _ = create_service(monkeypatch)

    url = service.add_url(
        1,
        "https://example.com/prueba"
    )

    result = service.get_url(url.id)

    assert result is url
    assert result.id == url.id
    assert result.url == "https://example.com/prueba"


def test_get_unknown_url_returns_none(monkeypatch):

    service, _, _ = create_service(monkeypatch)

    assert service.get_url(999) is None


def test_get_url_without_id_fails(monkeypatch):

    service, _, _ = create_service(monkeypatch)

    try:
        service.get_url(None)
        assert False
    except ValueError as error:
        assert str(error) == "El ID de la URL es obligatorio"


def test_normalize_url_none():

    assert UrlService._normalize_url(None) == ""


def test_normalize_url_strips_spaces():

    assert (
        UrlService._normalize_url(
            "  https://example.com/prueba  "
        )
        == "https://example.com/prueba"
    )


def test_normalize_url_converts_value_to_string():

    assert UrlService._normalize_url(12345) == "12345"


def test_normalize_url_extracts_markdown_value():

    result = UrlService._normalize_url(
        "[Texto](https://example.com/prueba)"
    )

    assert result == "Texto"


def test_normalize_url_invalid_markdown_is_preserved():

    value = "[Texto sin cierre"

    assert UrlService._normalize_url(value) == value


def test_normalize_host_with_https():

    assert (
        UrlService._normalize_host(
            "https://Example.COM/"
        )
        == "example.com"
    )


def test_normalize_host_with_http():

    assert (
        UrlService._normalize_host(
            "http://Example.COM/"
        )
        == "example.com"
    )


def test_normalize_host_without_scheme():

    assert (
        UrlService._normalize_host(
            "Example.COM/"
        )
        == "example.com"
    )


def test_normalize_host_with_trailing_dot():

    assert (
        UrlService._normalize_host(
            "example.com."
        )
        == "example.com"
    )


def test_normalize_host_empty_value():

    assert UrlService._normalize_host("") == ""


def test_normalize_host_none():

    assert UrlService._normalize_host(None) == ""


def test_validate_url_domain_accepts_matching_domain():

    UrlService._validate_url_domain(
        "https://example.com/prueba",
        "example.com"
    )


def test_validate_url_domain_accepts_case_difference():

    UrlService._validate_url_domain(
        "https://EXAMPLE.COM/prueba",
        "example.com"
    )


def test_validate_url_domain_rejects_invalid_url_host():

    try:
        UrlService._validate_url_domain(
            "not a valid url",
            "example.com"
        )
        assert False
    except ValueError as error:
        assert str(error) == "La URL no contiene un dominio válido"


def test_validate_url_domain_rejects_invalid_selected_domain():

    try:
        UrlService._validate_url_domain(
            "https://example.com/prueba",
            "not a valid domain"
        )
        assert False
    except ValueError as error:
        assert str(error) == "El dominio seleccionado no es válido"


def test_validate_url_domain_rejects_different_domain():

    try:
        UrlService._validate_url_domain(
            "https://example.org/prueba",
            "example.com"
        )
        assert False
    except ValueError as error:
        message = str(error)

        assert "no pertenece al dominio seleccionado" in message
        assert "example.com" in message
        assert "example.org" in message

def test_normalize_host_rejects_internal_spaces():

    assert UrlService._normalize_host(
        "example .com"
    ) == ""


def test_normalize_host_rejects_single_label():

    assert UrlService._normalize_host(
        "localhost"
    ) == ""


def test_normalize_host_rejects_consecutive_dots():

    assert UrlService._normalize_host(
        "example..com"
    ) == ""


def test_validate_url_domain_rejects_invalid_url_host_with_no_dot():

    try:
        UrlService._validate_url_domain(
            "https://localhost/prueba",
            "example.com"
        )
        assert False
    except ValueError as error:
        assert str(error) == "La URL no contiene un dominio válido"


def test_update_url_normalizes_markdown_url(monkeypatch):

    service, _, _ = create_service(monkeypatch)

    url = service.add_url(
        1,
        "https://example.com/antigua"
    )

    url.url = "[https://example.com/nueva](https://example.com/nueva)"

    result = service.update_url(url)

    assert result is True
    assert url.url == "https://example.com/nueva"
    assert url.status == "PENDIENTE"
    assert url.response_code is None
    assert url.response_message == ""


def test_update_url_keeps_selected_domain(monkeypatch):

    service, _, _ = create_service(monkeypatch)

    url = service.add_url(
        1,
        "https://example.com/prueba"
    )

    url.domain_id = 1
    url.url = "https://example.com/otra"

    result = service.update_url(url)

    assert result is True
    assert url.domain_id == 1
    assert url.url == "https://example.com/otra"



