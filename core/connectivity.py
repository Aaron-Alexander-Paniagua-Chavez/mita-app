"""Detección breve y no invasiva de conectividad para MITA."""
from __future__ import annotations

from dataclasses import dataclass
import socket


@dataclass(frozen=True)
class EstadoRed:
    internet: bool
    red_local: bool
    direccion_local: str = ""

    @property
    def descripcion(self) -> str:
        if self.internet:
            return "Con internet"
        if self.red_local:
            return "Sólo red local"
        return "Sin red"


def comprobar_red(timeout: float = 0.8) -> EstadoRed:
    """No transmite datos; sólo determina si hay ruta local e internet."""
    direccion = ""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.settimeout(timeout)
            s.connect(("1.1.1.1", 53))
            direccion = s.getsockname()[0]
    except OSError:
        try:
            direccion = socket.gethostbyname(socket.gethostname())
        except OSError:
            direccion = ""

    red_local = bool(direccion and not direccion.startswith("127."))
    try:
        with socket.create_connection(("one.one.one.one", 443), timeout=timeout):
            return EstadoRed(True, red_local, direccion)
    except OSError:
        return EstadoRed(False, red_local, direccion)
