import json
import urllib.request
import urllib.error
from urllib.parse import urlparse


class IndexNowService:

    ENDPOINT = "https://api.indexnow.org/indexnow"

    def submit(self, host, key, url):

        if not host:
            raise ValueError("El host es obligatorio")

        if not key:
            raise ValueError("La API key es obligatoria")

        if not url:
            raise ValueError("La URL es obligatoria")

        # Normalizar el dominio para IndexNow.
        # Acepta:
        # https://dominio.com/
        # http://dominio.com/
        # dominio.com
        # y devuelve:
        # dominio.com

        host = host.strip()

        if "://" in host:
            parsed = urlparse(host)
            host = parsed.netloc
        else:
            host = host.rstrip("/")

        if not host:
            raise ValueError("El host no es válido")

        payload = {
            "host": host,
            "key": key.strip(),
            "urlList": [
                url.strip()
            ]
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