import json
import urllib.request
import urllib.error
from urllib.parse import urlparse


class IndexNowService:

    ENDPOINT = "https://api.indexnow.org/indexnow"

    def _normalize_host(self, host):
        if not host:
            raise ValueError("El host es obligatorio")

        host = host.strip()

        if "://" in host:
            parsed = urlparse(host)
            host = parsed.netloc
        else:
            host = host.rstrip("/")

        if not host:
            raise ValueError("El host no es válido")

        return host

    def _send(self, host, key, urls):
        if not key:
            raise ValueError("La API key es obligatoria")

        if not urls:
            raise ValueError("Debe existir al menos una URL")

        host = self._normalize_host(host)

        key = key.strip()

        clean_urls = [
            url.strip()
            for url in urls
            if url and url.strip()
        ]

        if not clean_urls:
            raise ValueError("No hay URLs válidas para enviar")

        payload = {
            "host": host,
            "key": key,
            "urlList": clean_urls
        }

        data = json.dumps(payload).encode("utf-8")

        request = urllib.request.Request(
            self.ENDPOINT,
            data=data,
            headers={
                "Content-Type": "application/json; charset=utf-8"
            },
            method="POST"
        )

        try:

            with urllib.request.urlopen(
                request,
                timeout=15
            ) as response:

                return {
                    "status_code": response.status,
                    "message": response.read().decode(
                        "utf-8",
                        errors="replace"
                    )
                }

        except urllib.error.HTTPError as error:

            return {
                "status_code": error.code,
                "message": error.read().decode(
                    "utf-8",
                    errors="replace"
                )
            }

        except urllib.error.URLError as error:

            return {
                "status_code": None,
                "message": str(error.reason)
            }

    def submit(self, host, key, url):

        if not url:
            raise ValueError("La URL es obligatoria")

        return self._send(
            host,
            key,
            [url]
        )

    def submit_batch(self, host, key, urls):

        return self._send(
            host,
            key,
            urls
        )