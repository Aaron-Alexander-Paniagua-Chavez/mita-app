"""Configuración central de MITA.

Las credenciales pertenecen al entorno, nunca al repositorio. Copia
``.env.example`` a ``.env`` o define las variables antes de iniciar la app.
"""
from __future__ import annotations

import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None


APP_ROOT = Path(__file__).resolve().parents[1]
if load_dotenv:
    load_dotenv(APP_ROOT / ".env")


# Paleta oficial MITA: cada tupla contiene (modo claro, modo oscuro).
BG_COLOR = ("#F9F8F4", "#15211D")
BG_WARM = ("#DAB7A3", "#4B342B")
ACCENT_GREEN = ("#21574A", "#75B8A3")
ACCENT_GREEN_LIGHT = ("#628272", "#477D6C")
ACCENT_TERRACOTA = ("#D39B75", "#E8AA82")
SOFT_GREEN = ("#E8F0E8", "#23372F")
SOFT_PURPLE = ("#F0E8F0", "#372F3D")
SURFACE_COLOR = ("#FFFFFF", "#22312B")
DISABLED_SURFACE = ("#EEEEEE", "#384840")
TEXT_GRAY = ("#5A5A5A", "#C4D0C9")
DARK_TEXT = ("#1A1A1A", "#F4F8F5")
BORDER_SAGE = ("#9CA18D", "#71857A")
ERROR_COLOR = ("#D32F2F", "#FF8983")
WHITE = ("#FFFFFF", "#F4F8F5")

# Accesibilidad (RNF01–RNF03): mínimo 16px, alto contraste
FONT_FAMILY = "Segoe UI"
FONT_SIZE_BODY = 16
FONT_SIZE_BUTTON = 18
FONT_SIZE_SUBTITLE = 24
FONT_SIZE_TITLE = 32
FONT_SIZE_HERO = 36
BUTTON_HEIGHT = 52
BUTTON_HEIGHT_LARGE = 64
ENTRY_HEIGHT = 50


def _int_env(name: str, default: int) -> int:
    """Obtiene un entero del entorno sin impedir que la interfaz inicie."""
    try:
        return int(os.getenv(name, default))
    except ValueError:
        return default


# Persistencia. Los valores por defecto permiten desarrollo local sin secretos.
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = _int_env("MYSQL_PORT", 3306)
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "SistemaGeriatrico")
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DATABASE = os.getenv("MONGO_DATABASE", "mita_analytics")

MYSQL_CONFIG = {
    "host": MYSQL_HOST,
    "port": MYSQL_PORT,
    "user": MYSQL_USER,
    "password": MYSQL_PASSWORD,
    "database": MYSQL_DATABASE,
    "charset": "utf8mb4",
    "use_unicode": True,
    "connection_timeout": 3,
}

# Panel admin secreto: Ctrl+Shift+A
ADMIN_SECRET_COMBO = "<Control-Shift-A>"
