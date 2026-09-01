from models.domain import Domain
from models.url import UrlRecord
from services.dashboard_service import DashboardService


class FakeDomainRepository:

    def __init__(self, domains=None):
        self.domains = domains or []

    def get_all(self):
        return list(self.domains)


class FakeUrlRepository:

    def __init__(self, urls=None):
        self.urls = urls or []

    def get_all(self):
        return list(self.urls)


def create_service(monkeypatch, domains=None, urls=None):

    domain_repository = FakeDomainRepository(domains)
    url_repository = FakeUrlRepository(urls)

    monkeypatch.setattr(
        "services.dashboard_service.DomainRepository",
        lambda: domain_repository
    )

    monkeypatch.setattr(
        "services.dashboard_service.UrlRepository",
        lambda: url_repository
    )

    return DashboardService()


def test_get_statistics_with_empty_data(monkeypatch):

    service = create_service(monkeypatch)

    result = service.get_statistics()

    assert result == {
        "total_domains": 0,
        "active_domains": 0,
        "total_urls": 0,
        "pending_urls": 0,
        "successful_urls": 0,
        "error_urls": 0,
    }


def test_counts_active_and_inactive_domains(monkeypatch):

    domains = [
        Domain(
            id=1,
            domain="example.com",
            api_key="KEY",
            enabled=True
        ),
        Domain(
            id=2,
            domain="example.org",
            api_key="KEY",
            enabled=False
        ),
        Domain(
            id=3,
            domain="example.net",
            api_key="KEY",
            enabled=True
        ),
    ]

    service = create_service(
        monkeypatch,
        domains=domains
    )

    result = service.get_statistics()

    assert result["total_domains"] == 3
    assert result["active_domains"] == 2


def test_counts_total_and_pending_urls(monkeypatch):

    urls = [
        UrlRecord(
            id=1,
            domain_id=1,
            url="https://example.com/uno",
            status="PENDIENTE",
            response_code=None,
            response_message=""
        ),
        UrlRecord(
            id=2,
            domain_id=1,
            url="https://example.com/dos",
            status="ENVIADA",
            response_code=200,
            response_message=""
        ),
        UrlRecord(
            id=3,
            domain_id=1,
            url="https://example.com/tres",
            status="PENDIENTE",
            response_code=None,
            response_message=""
        ),
    ]

    service = create_service(
        monkeypatch,
        urls=urls
    )

    result = service.get_statistics()

    assert result["total_urls"] == 3
    assert result["pending_urls"] == 2


def test_counts_successful_2xx_responses(monkeypatch):

    urls = [
        UrlRecord(
            id=1,
            domain_id=1,
            url="https://example.com/200",
            status="ENVIADA",
            response_code=200,
            response_message=""
        ),
        UrlRecord(
            id=2,
            domain_id=1,
            url="https://example.com/201",
            status="ENVIADA",
            response_code=201,
            response_message=""
        ),
        UrlRecord(
            id=3,
            domain_id=1,
            url="https://example.com/202",
            status="ENVIADA",
            response_code=202,
            response_message=""
        ),
    ]

    service = create_service(
        monkeypatch,
        urls=urls
    )

    result = service.get_statistics()

    assert result["successful_urls"] == 3
    assert result["error_urls"] == 0


def test_counts_error_responses(monkeypatch):

    urls = [
        UrlRecord(
            id=1,
            domain_id=1,
            url="https://example.com/400",
            status="ERROR",
            response_code=400,
            response_message=""
        ),
        UrlRecord(
            id=2,
            domain_id=1,
            url="https://example.com/404",
            status="ERROR",
            response_code=404,
            response_message=""
        ),
        UrlRecord(
            id=3,
            domain_id=1,
            url="https://example.com/500",
            status="ERROR",
            response_code=500,
            response_message=""
        ),
    ]

    service = create_service(
        monkeypatch,
        urls=urls
    )

    result = service.get_statistics()

    assert result["error_urls"] == 3
    assert result["successful_urls"] == 0


def test_3xx_responses_are_not_success_or_error(monkeypatch):

    urls = [
        UrlRecord(
            id=1,
            domain_id=1,
            url="https://example.com/301",
            status="ENVIADA",
            response_code=301,
            response_message=""
        ),
        UrlRecord(
            id=2,
            domain_id=1,
            url="https://example.com/304",
            status="ENVIADA",
            response_code=304,
            response_message=""
        ),
    ]

    service = create_service(
        monkeypatch,
        urls=urls
    )

    result = service.get_statistics()

    assert result["successful_urls"] == 0
    assert result["error_urls"] == 0


def test_complete_dashboard_statistics(monkeypatch):

    domains = [
        Domain(
            id=1,
            domain="example.com",
            api_key="KEY",
            enabled=True
        ),
        Domain(
            id=2,
            domain="example.org",
            api_key="KEY",
            enabled=False
        ),
        Domain(
            id=3,
            domain="example.net",
            api_key="KEY",
            enabled=True
        ),
    ]

    urls = [
        UrlRecord(
            id=1,
            domain_id=1,
            url="https://example.com/pendiente",
            status="PENDIENTE",
            response_code=None,
            response_message=""
        ),
        UrlRecord(
            id=2,
            domain_id=1,
            url="https://example.com/ok",
            status="ENVIADA",
            response_code=200,
            response_message=""
        ),
        UrlRecord(
            id=3,
            domain_id=2,
            url="https://example.org/aceptada",
            status="ENVIADA",
            response_code=202,
            response_message=""
        ),
        UrlRecord(
            id=4,
            domain_id=3,
            url="https://example.net/error",
            status="ERROR",
            response_code=500,
            response_message=""
        ),
        UrlRecord(
            id=5,
            domain_id=3,
            url="https://example.net/redireccion",
            status="ENVIADA",
            response_code=301,
            response_message=""
        ),
    ]

    service = create_service(
        monkeypatch,
        domains=domains,
        urls=urls
    )

    result = service.get_statistics()

    assert result == {
        "total_domains": 3,
        "active_domains": 2,
        "total_urls": 5,
        "pending_urls": 1,
        "successful_urls": 2,
        "error_urls": 1,
    }
