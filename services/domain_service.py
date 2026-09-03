from models.domain import Domain
from repositories.domain_repository import DomainRepository


class DomainService:

    def __init__(self):
        self.repository = DomainRepository()

    def get_domains(self):
        return self.repository.get_all()

    def get_domain(self, domain_id):
        if domain_id is None:
            raise ValueError("El ID del dominio es obligatorio")

        return self.repository.get_by_id(domain_id)

    def add_domain(self, domain, api_key="", enabled=True):
        domain_name = self._normalize_domain(domain)

        if not domain_name:
            raise ValueError("El dominio no puede estar vacío")

        if self._domain_exists(domain_name):
            raise ValueError(f"El dominio '{domain_name}' ya existe")

        new_domain = Domain(
            domain=domain_name,
            api_key=api_key or "",
            enabled=bool(enabled)
        )

        return self.repository.create(new_domain)

    def update_domain(self, domain):
        if not isinstance(domain, Domain):
            raise TypeError("Se esperaba un objeto Domain")

        if domain.id is None:
            raise ValueError("El dominio debe tener un ID")

        existing = self.repository.get_by_id(domain.id)

        if existing is None:
            raise ValueError("El dominio no existe")

        domain_name = self._normalize_domain(domain.domain)

        if not domain_name:
            raise ValueError("El dominio no puede estar vacío")

        for item in self.repository.get_all():
            if item.id != domain.id and item.domain.lower() == domain_name:
                raise ValueError(
                    f"El dominio '{domain_name}' ya existe"
                )

        domain.domain = domain_name
        domain.api_key = domain.api_key or ""
        domain.enabled = bool(domain.enabled)

        return self.repository.update(domain)

    def delete_domain(self, domain_id):
        if domain_id is None:
            raise ValueError("El ID del dominio es obligatorio")

        return self.repository.delete(domain_id)

    def _domain_exists(self, domain_name):
        return any(
            item.domain.lower() == domain_name.lower()
            for item in self.repository.get_all()
        )

    @staticmethod
    def _normalize_domain(domain):
        if domain is None:
            return ""

        domain = domain.strip()

        if not domain or any(char.isspace() for char in domain):
            return ""

        return domain.lower()
