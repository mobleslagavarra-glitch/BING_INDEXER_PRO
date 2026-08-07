"""
Validador de URLs
"""

from urllib.parse import urlparse


class URLManager:

    @staticmethod
    def validate(url):

        try:

            data = urlparse(url)

            return bool(

                data.scheme

                and data.netloc

            )

        except Exception:

            return False