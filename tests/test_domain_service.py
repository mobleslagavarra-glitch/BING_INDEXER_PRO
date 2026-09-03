from services.domain_service import DomainService


class FakeRepository:

    def __init__(self):
        self.domains = []
        self.next_id = 1

    def get_all(self):
        return list(self.domains)

    def get_by_id(self, domain_id):
        for domain in self.domains:
            if domain.id == domain_id:
                return domain
        return None

    def create(self, domain):
        domain.id = self.next_id
        self.next_id += 1
        self.domains.append(domain)
        return domain

    def update(self, domain):
        for index, item in enumerate(self.domains):
            if item.id == domain.id:
                self.domains[index] = domain
                return True
        return False

    def delete(self, domain_id):
        original_length = len(self.domains)

        self.domains = [
            domain
            for domain in self.domains
            if domain.id != domain_id
        ]

        return len(self.domains) < original_length


def create_service(monkeypatch):
    repository = FakeRepository()

    monkeypatch.setattr(
        "services.domain_service.DomainRepository",
        lambda: repository
    )

    return DomainService()


def test_add_domain_normalizes_name(monkeypatch):
    service = create_service(monkeypatch)

    domain = service.add_domain(
        "  Example.COM  ",
        "TEST_KEY",
        True
    )

    assert domain.domain == "example.com"
    assert domain.api_key == "TEST_KEY"
    assert domain.enabled is True


def test_add_empty_domain_fails(monkeypatch):
    service = create_service(monkeypatch)

    try:
        service.add_domain("   ")
        assert False
    except ValueError as error:
        assert str(error) == "El dominio no puede estar vacío"


def test_duplicate_domain_fails(monkeypatch):
    service = create_service(monkeypatch)

    service.add_domain("example.com")

    try:
        service.add_domain("EXAMPLE.COM")
        assert False
    except ValueError as error:
        assert "ya existe" in str(error)


def test_update_domain(monkeypatch):
    service = create_service(monkeypatch)

    domain = service.add_domain(
        "example.com",
        "OLD_KEY",
        True
    )

    domain.domain = "  Example.ORG  "
    domain.api_key = "NEW_KEY"
    domain.enabled = False

    result = service.update_domain(domain)

    assert result is True
    assert domain.domain == "example.org"
    assert domain.api_key == "NEW_KEY"
    assert domain.enabled is False


def test_delete_domain(monkeypatch):
    service = create_service(monkeypatch)

    domain = service.add_domain("example.com")

    assert service.delete_domain(domain.id) is True
    assert service.get_domain(domain.id) is None
def test_get_domains_returns_all_domains(monkeypatch):
    service = create_service(monkeypatch)

    first = service.add_domain("example.com")
    second = service.add_domain("example.org")

    domains = service.get_domains()

    assert len(domains) == 2
    assert domains[0].domain == "example.com"
    assert domains[1].domain == "example.org"


def test_get_domain_returns_domain(monkeypatch):
    service = create_service(monkeypatch)

    domain = service.add_domain("example.com")

    result = service.get_domain(domain.id)

    assert result is domain


def test_get_domain_without_id_fails(monkeypatch):
    service = create_service(monkeypatch)

    try:
        service.get_domain(None)
        assert False
    except ValueError as error:
        assert str(error) == "El ID del dominio es obligatorio"


def test_get_domain_missing_returns_none(monkeypatch):
    service = create_service(monkeypatch)

    assert service.get_domain(999) is None


def test_add_domain_without_api_key_uses_empty_string(monkeypatch):
    service = create_service(monkeypatch)

    domain = service.add_domain(
        "example.com",
        None,
        True
    )

    assert domain.api_key == ""
    assert domain.enabled is True


def test_add_domain_disabled(monkeypatch):
    service = create_service(monkeypatch)

    domain = service.add_domain(
        "example.com",
        "TEST_KEY",
        False
    )

    assert domain.enabled is False


def test_update_domain_requires_domain_object(monkeypatch):
    service = create_service(monkeypatch)

    try:
        service.update_domain("example.com")
        assert False
    except TypeError as error:
        assert str(error) == "Se esperaba un objeto Domain"


def test_update_domain_requires_id(monkeypatch):
    from models.domain import Domain

    service = create_service(monkeypatch)

    domain = Domain(
        id=None,
        domain="example.com",
        api_key="TEST_KEY",
        enabled=True
    )

    try:
        service.update_domain(domain)
        assert False
    except ValueError as error:
        assert str(error) == "El dominio debe tener un ID"


def test_update_missing_domain_fails(monkeypatch):
    from models.domain import Domain

    service = create_service(monkeypatch)

    domain = Domain(
        id=999,
        domain="example.com",
        api_key="TEST_KEY",
        enabled=True
    )

    try:
        service.update_domain(domain)
        assert False
    except ValueError as error:
        assert str(error) == "El dominio no existe"


def test_update_duplicate_domain_fails(monkeypatch):
    service = create_service(monkeypatch)

    first = service.add_domain("example.com")
    second = service.add_domain("example.org")

    second.domain = "EXAMPLE.COM"

    try:
        service.update_domain(second)
        assert False
    except ValueError as error:
        assert "ya existe" in str(error)

    assert first.domain == "example.com"


def test_update_empty_domain_fails(monkeypatch):
    service = create_service(monkeypatch)

    domain = service.add_domain("example.com")
    domain.domain = "   "

    try:
        service.update_domain(domain)
        assert False
    except ValueError as error:
        assert str(error) == "El dominio no puede estar vacío"


def test_delete_domain_without_id_fails(monkeypatch):
    service = create_service(monkeypatch)

    try:
        service.delete_domain(None)
        assert False
    except ValueError as error:
        assert str(error) == "El ID del dominio es obligatorio"


def test_add_none_domain_fails(monkeypatch):

    service = create_service(monkeypatch)

    try:
        service.add_domain(None)
        assert False
    except ValueError as error:
        assert str(error) == "El dominio no puede estar vacío"


def test_add_domain_with_internal_spaces_fails(monkeypatch):

    service = create_service(monkeypatch)

    try:
        service.add_domain("example .com")
        assert False
    except ValueError as error:
        assert str(error) == "El dominio no puede estar vacío"


def test_update_domain_without_api_key_uses_empty_string(
    monkeypatch
):

    service = create_service(monkeypatch)

    domain = service.add_domain(
        "example.com",
        "OLD_KEY",
        True
    )

    domain.api_key = None

    result = service.update_domain(domain)

    assert result is True
    assert domain.api_key == ""


def test_update_domain_converts_enabled_to_boolean(
    monkeypatch
):

    service = create_service(monkeypatch)

    domain = service.add_domain(
        "example.com",
        "TEST_KEY",
        True
    )

    domain.enabled = 0

    result = service.update_domain(domain)

    assert result is True
    assert domain.enabled is False


def test_delete_missing_domain_returns_false(monkeypatch):

    service = create_service(monkeypatch)

    assert service.delete_domain(999) is False

