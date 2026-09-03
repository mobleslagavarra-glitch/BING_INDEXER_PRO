import json
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

    assert service._normalize_host(
        "  example.com/  "
    ) == "example.com"


def test_normalize_host_with_http():

    service = IndexNowService()

    assert service._normalize_host(
        "http://example.com"
    ) == "example.com"


def test_normalize_host_empty_fails():

    service = IndexNowService()

    try:
        service._normalize_host("")
        assert False
    except ValueError as error:
        assert "obligatorio" in str(error)


def test_normalize_host_none_fails():

    service = IndexNowService()

    try:
        service._normalize_host(None)
        assert False
    except ValueError as error:
        assert "obligatorio" in str(error)


def test_normalize_host_invalid_url_fails():

    service = IndexNowService()

    try:
        service._normalize_host("https:///")
        assert False
    except ValueError as error:
        assert "válido" in str(error)


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


def test_submit_none_url_fails():

    service = IndexNowService()

    try:
        service.submit(
            "example.com",
            "TEST_KEY",
            None
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


def test_submit_batch_none_urls_fails():

    service = IndexNowService()

    try:
        service.submit_batch(
            "example.com",
            "TEST_KEY",
            None
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


def test_submit_none_api_key_fails():

    service = IndexNowService()

    try:
        service.submit(
            "example.com",
            None,
            "https://example.com/prueba"
        )
        assert False
    except ValueError as error:
        assert "API key" in str(error)


def test_submit_batch_cleans_api_key_and_urls(monkeypatch):

    captured = {}

    def fake_urlopen(request, timeout):

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
        "example.com",
        "  TEST_KEY  ",
        [
            " https://example.com/uno ",
            "",
            None,
            "   ",
            "https://example.com/dos"
        ]
    )

    assert result["success"] is True

    payload = json.loads(
        captured["data"].decode("utf-8")
    )

    assert payload["key"] == "TEST_KEY"

    assert payload["urlList"] == [
        "https://example.com/uno",
        "https://example.com/dos"
    ]


def test_submit_batch_all_invalid_urls_fails():

    service = IndexNowService()

    try:
        service.submit_batch(
            "example.com",
            "TEST_KEY",
            ["", " ", None]
        )
        assert False
    except ValueError as error:
        assert "URLs válidas" in str(error)


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

    payload = json.loads(
        captured["data"].decode("utf-8")
    )

    assert payload["host"] == "example.com"
    assert payload["key"] == "TEST_KEY"
    assert payload["urlList"] == [
        "https://example.com/uno",
        "https://example.com/dos"
    ]


def test_submit_batch_request_headers_and_method(monkeypatch):

    captured = {}

    def fake_urlopen(request, timeout):

        captured["method"] = request.get_method()
        captured["content_type"] = request.get_header(
            "Content-type"
        )

        return FakeResponse(202, "OK")

    monkeypatch.setattr(
        "services.indexnow_service.urllib.request.urlopen",
        fake_urlopen
    )

    service = IndexNowService()

    service.submit_batch(
        "example.com",
        "TEST_KEY",
        ["https://example.com/prueba"]
    )

    assert captured["method"] == "POST"
    assert captured["content_type"] == (
        "application/json; charset=utf-8"
    )


def test_submit_batch_http_200(monkeypatch):

    def fake_urlopen(request, timeout):

        return FakeResponse(200, "OK")

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

    assert result["success"] is True
    assert result["status_code"] == 200
    assert result["message"] == "OK"


def test_submit_batch_http_202(monkeypatch):

    def fake_urlopen(request, timeout):

        return FakeResponse(202, "Aceptado")

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

    assert result["success"] is True
    assert result["status_code"] == 202


def test_submit_batch_unexpected_status(monkeypatch):

    def fake_urlopen(request, timeout):

        return FakeResponse(201, "Created")

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
    assert result["status_code"] == 201
    assert result["message"] == "Created"


def test_submit_batch_http_error(monkeypatch):

    def fake_urlopen(request, timeout):

        error = urllib.error.HTTPError(
            request.full_url,
            400,
            "Bad Request",
            {},
            None
        )

        error.read = lambda: b"Solicitud incorrecta"

        raise error

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
    assert result["message"] == "Solicitud incorrecta"


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

    payload = json.loads(
        captured["data"].decode("utf-8")
    )

    assert payload["urlList"] == [
        "https://example.com/prueba"
    ]


def test_submit_batch_single_url(monkeypatch):

    captured = {}

    def fake_urlopen(request, timeout):

        captured["data"] = request.data

        return FakeResponse(202, "Aceptado")

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

    payload = json.loads(
        captured["data"].decode("utf-8")
    )

    assert result["success"] is True
    assert payload["urlList"] == [
        "https://example.com/prueba"
    ]

def test_normalize_host_https_with_path():

    service = IndexNowService()

    assert service._normalize_host(
        "https://example.com/ruta/prueba"
    ) == "example.com"


def test_normalize_host_http_with_path():

    service = IndexNowService()

    assert service._normalize_host(
        "http://example.com/ruta"
    ) == "example.com"


def test_normalize_host_converts_value_to_string():

    service = IndexNowService()

    assert service._normalize_host(
        12345
    ) == "12345"


def test_normalize_host_scheme_without_domain_fails():

    service = IndexNowService()

    try:
        service._normalize_host(
            "https://"
        )
        assert False
    except ValueError as error:
        assert str(error) == "El host no es válido"


def test_submit_batch_replaces_invalid_utf8(monkeypatch):

    class InvalidUtf8Response:

        status = 202

        def read(self):
            return b"Respuesta \xff"

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            pass

    def fake_urlopen(request, timeout):

        return InvalidUtf8Response()

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

    assert result["success"] is True
    assert result["status_code"] == 202
    assert "Respuesta" in result["message"]
    assert "\ufffd" in result["message"]
