"""Configuración central de MITA.

Las credenciales pertenecen al entorno, nunca al repositorio. Copia
``.env.example`` a ``.env`` o define las variables antes de iniciar la app.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


APP_ROOT = Path(__file__).resolve().parents[1]

APP_DATA_ROOT = Path(os.getenv("LOCALAPPDATA") or Path.home()) / "MITA"
DATABASE_SETTINGS_PATH = APP_DATA_ROOT / "database.json"
SESSION_SETTINGS_PATH = APP_DATA_ROOT / "session.json"


def _cargar_archivo_env() -> None:
    """Carga ``.env`` local sin sobrescribir variables ya definidas.

    La aplicación se puede distribuir sin este archivo. Mantener la lectura
    aquí hace que el ``.env`` existente sí sea útil, sin exigir que se suba al
    repositorio ni añadir una dependencia para ello.
    """
    ruta = APP_ROOT / ".env"
    try:
        for linea in ruta.read_text(encoding="utf-8").splitlines():
            linea = linea.strip()
            if not linea or linea.startswith("#") or "=" not in linea:
                continue
            nombre, valor = linea.split("=", 1)
            nombre = nombre.strip()
            if nombre and nombre not in os.environ:
                os.environ[nombre] = valor.strip().strip('"').strip("'")
    except OSError:
        pass


_cargar_archivo_env()


def _leer_configuracion_local() -> dict[str, Any]:
    try:
        with DATABASE_SETTINGS_PATH.open("r", encoding="utf-8") as archivo:
            data = json.load(archivo)
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def guardar_configuracion_mysql(
    host: str,
    port: int,
    database: str,
    user: str,
    password: str,
    admin_user: str,
    admin_password: str,
) -> None:
    APP_DATA_ROOT.mkdir(parents=True, exist_ok=True)
    data = {
        "MYSQL_HOST": host,
        "MYSQL_PORT": int(port),
        "MYSQL_DATABASE": database,
        "MYSQL_USER": user,
        "MYSQL_PASSWORD": password,
        "MYSQL_ADMIN_USER": admin_user,
        "MYSQL_ADMIN_PASSWORD": admin_password,
    }
    with DATABASE_SETTINGS_PATH.open("w", encoding="utf-8") as archivo:
        json.dump(data, archivo, indent=2)
    try:
        DATABASE_SETTINGS_PATH.chmod(0o600)
    except OSError:
        pass


_CONFIG_LOCAL = _leer_configuracion_local()


def _valor_configuracion(nombre: str, predeterminado: Any) -> Any:
    return os.getenv(nombre, _CONFIG_LOCAL.get(nombre, predeterminado))


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
# Inter es la tipografía de producto. Windows la usa si está instalada; si no,
# Tk aplica su fallback de sistema sin impedir el arranque.
FONT_FAMILY = "Inter"
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
MYSQL_HOST = _valor_configuracion("MYSQL_HOST", "127.0.0.1")
MYSQL_PORT = _int_env("MYSQL_PORT", _CONFIG_LOCAL.get("MYSQL_PORT", 3306))
MYSQL_DATABASE = _valor_configuracion("MYSQL_DATABASE", "SistemaGeriatrico")
MYSQL_USER = _valor_configuracion("MYSQL_USER", "root")
MYSQL_PASSWORD = _valor_configuracion("MYSQL_PASSWORD", "")
MYSQL_ADMIN_USER = _valor_configuracion("MYSQL_ADMIN_USER", MYSQL_USER)
MYSQL_ADMIN_PASSWORD = _valor_configuracion("MYSQL_ADMIN_PASSWORD", MYSQL_PASSWORD)

MONGO_URI = _valor_configuracion("MONGO_URI", "mongodb://127.0.0.1:27017")
MONGO_DATABASE = _valor_configuracion("MONGO_DATABASE", "mita_analytics")

# Funciones remotas opcionales. Nunca se escriben claves en el código ni se
# mandan datos clínicos a estas integraciones.
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()
MQTT_HOST = os.getenv("MQTT_HOST", "").strip()
MQTT_PORT = _int_env("MQTT_PORT", 8883)
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "").strip()
MQTT_TLS = os.getenv("MQTT_TLS", "1").strip().lower() not in {"0", "false", "no"}
MITA_DEMO_PASSWORD = os.getenv("MITA_DEMO_PASSWORD", "")

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

MYSQL_ADMIN_CONFIG = {
    "host": MYSQL_HOST,
    "port": MYSQL_PORT,
    "user": MYSQL_ADMIN_USER,
    "password": MYSQL_ADMIN_PASSWORD,
    "charset": "utf8mb4",
    "use_unicode": True,
    "connection_timeout": 3,
}

# Panel admin secreto: Ctrl+Shift+A
ADMIN_SECRET_COMBO = "<Control-Shift-A>"
