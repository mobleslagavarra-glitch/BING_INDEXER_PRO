from pathlib import Path
from loguru import logger

from core.paths import LOGS

LOG_FILE = LOGS / "bing_indexer.log"

logger.remove()

logger.add(
    LOG_FILE,
    rotation="5 MB",
    retention=10,
    level="INFO",
    encoding="utf-8"
)