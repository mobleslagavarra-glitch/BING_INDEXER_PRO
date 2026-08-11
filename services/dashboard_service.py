from repositories.domain_repository import DomainRepository
from repositories.url_repository import UrlRepository


class DashboardService:

    def __init__(self):
        self.domain_repository = DomainRepository()
        self.url_repository = UrlRepository()

    def get_statistics(self):
        domains = self.domain_repository.get_all()
        urls = self.url_repository.get_all()

        total_domains = len(domains)

        active_domains = sum(
            1 for domain in domains
            if domain.enabled
        )

        total_urls = len(urls)

        pending_urls = sum(
            1 for url in urls
            if url.status == "PENDIENTE"
        )

        successful_urls = sum(
            1 for url in urls
            if url.response_code is not None
            and 200 <= url.response_code < 300
        )

        error_urls = sum(
            1 for url in urls
            if url.response_code is not None
            and url.response_code >= 400
        )

        return {
            "total_domains": total_domains,
            "active_domains": active_domains,
            "total_urls": total_urls,
            "pending_urls": pending_urls,
            "successful_urls": successful_urls,
            "error_urls": error_urls,
        }
