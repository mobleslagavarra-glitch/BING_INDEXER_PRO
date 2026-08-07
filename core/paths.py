from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

DATABASE = ROOT / "database"
CONFIG = ROOT / "config"
LOGS = ROOT / "logs"
REPORTS = ROOT / "reports"
INPUT = ROOT / "input"
OUTPUT = ROOT / "output"
BACKUP = ROOT / "backup"

FOLDERS = [
    DATABASE,
    CONFIG,
    LOGS,
    REPORTS,
    INPUT,
    OUTPUT,
    BACKUP,
]