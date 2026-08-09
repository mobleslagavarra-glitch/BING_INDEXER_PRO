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