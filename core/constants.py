"""
Constantes generales
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

CONFIG_DIR = ROOT / "config"

DATABASE_DIR = ROOT / "database"

LOG_DIR = ROOT / "logs"

INPUT_DIR = ROOT / "input"

OUTPUT_DIR = ROOT / "output"

REPORT_DIR = ROOT / "reports"

BACKUP_DIR = ROOT / "backup"