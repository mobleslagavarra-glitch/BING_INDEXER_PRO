"""
Sistema de logs
"""

from loguru import logger
from pathlib import Path

LOG_DIR = Path("logs")

LOG_DIR.mkdir(exist_ok=True)

logger.add(

    LOG_DIR / "app.log",

    rotation="5 MB",

    retention=10,

    encoding="utf-8"

)


class Logger:

    @staticmethod
    def info(text):

        logger.info(text)

    @staticmethod
    def warning(text):

        logger.warning(text)

    @staticmethod
    def error(text):

        logger.error(text)

    @staticmethod
    def success(text):

        logger.success(text)