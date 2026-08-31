import urllib.error

from services.indexnow_service import IndexNowService


class FakeResponse:

    def __init__(self, status=202, body="Aceptado"):
        self.status = status
        self.body = body

    def read(self):
        return self.body.encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass


def test_normalize_host():

    service = IndexNowService()

    assert service._normalize_host(
        "example.com"
    ) == "example.com"

    assert service._normalize_host(
        "https://example.com/"
    ) == "example.com"


def test_normalize_host_empty_fails():

    service = IndexNowService()

    try:
        service._normalize_host("")
        assert False
    except ValueError as error:
        assert "obligatorio" in str(error)


def test_submit_requires_url():

    service = IndexNowService()

    try:
        service.submit(
            "example.com",
            "TEST_KEY",
            ""
        )
        assert False
    except ValueError as error:
        assert "URL" in str(error)


def test_submit_batch_requires_urls():

    service = IndexNowService()

    try:
        service.submit_batch(
            "example.com",
            "TEST_KEY",
            []
        )
        assert False
    except ValueError as error:
        assert "URL" in str(error)


def test_submit_requires_api_key():

    service = IndexNowService()

    try:
        service.submit(
            "example.com",
            "",
            "https://example.com/prueba"
        )
        assert False
    except ValueError as error:
        assert "API key" in str(error)


def test_submit_batch_sends_all_urls(monkeypatch):

    captured = {}

    def fake_urlopen(request, timeout):

        captured["url"] = request.full_url
        captured["timeout"] = timeout
        captured["data"] = request.data

        return FakeResponse(
            202,
            "Aceptado"
        )

    monkeypatch.setattr(
        "services.indexnow_service.urllib.request.urlopen",
        fake_urlopen
    )

    service = IndexNowService()

    result = service.submit_batch(
        "https://example.com/",
        "TEST_KEY",
        [
            "https://example.com/uno",
            "https://example.com/dos"
        ]
    )

    assert result["success"] is True
    assert result["status_code"] == 202
    assert result["message"] == "Aceptado"

    assert captured["url"] == (
        "https://api.indexnow.org/indexnow"
    )

    assert captured["timeout"] == 15

    import json

    payload = json.loads(
        captured["data"].decode("utf-8")
    )

    assert payload["host"] == "example.com"
    assert payload["key"] == "TEST_KEY"
    assert payload["urlList"] == [
        "https://example.com/uno",
        "https://example.com/dos"
    ]


def test_submit_batch_http_error(monkeypatch):

    def fake_urlopen(request, timeout):

        raise urllib.error.HTTPError(
            request.full_url,
            400,
            "Bad Request",
            {},
            None
        )

    monkeypatch.setattr(
        "services.indexnow_service.urllib.request.urlopen",
        fake_urlopen
    )

    service = IndexNowService()

    result = service.submit_batch(
        "example.com",
        "TEST_KEY",
        ["https://example.com/prueba"]
    )

    assert result["success"] is False
    assert result["status_code"] == 400


def test_submit_batch_connection_error(monkeypatch):

    def fake_urlopen(request, timeout):

        raise urllib.error.URLError(
            "Sin conexión"
        )

    monkeypatch.setattr(
        "services.indexnow_service.urllib.request.urlopen",
        fake_urlopen
    )

    service = IndexNowService()

    result = service.submit_batch(
        "example.com",
        "TEST_KEY",
        ["https://example.com/prueba"]
    )

    assert result["success"] is False
    assert result["status_code"] is None
    assert "Sin conexión" in result["message"]


def test_submit_uses_single_url(monkeypatch):

    captured = {}

    def fake_urlopen(request, timeout):

        captured["data"] = request.data

        return FakeResponse(
            200,
            "OK"
        )

    monkeypatch.setattr(
        "services.indexnow_service.urllib.request.urlopen",
        fake_urlopen
    )

    service = IndexNowService()

    result = service.submit(
        "example.com",
        "TEST_KEY",
        "https://example.com/prueba"
    )

    assert result["success"] is True
    assert result["status_code"] == 200

    import json

    payload = json.loads(
        captured["data"].decode("utf-8")
    )

    assert payload["urlList"] == [
        "https://example.com/prueba"
    ]
