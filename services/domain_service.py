from repositories.domain_repository import DomainRepository


class DomainService:

    def __init__(self):

        self.repository = DomainRepository()

    def get_domains(self):

        return self.repository.get_all()