"""Medición local de tiempo de uso, sin recopilar contenido privado."""
from __future__ import annotations

from dataclasses import dataclass
from time import monotonic
from typing import Optional


@dataclass
class ActividadEnCurso:
    titulo: str
    categoria: str
    inicio: float


class TimeTrackingService:
    def __init__(self) -> None:
        self._inicio_sesion: Optional[float] = None
        self._actividad: Optional[ActividadEnCurso] = None

    def iniciar_sesion(self) -> None:
        self._inicio_sesion = monotonic()

    def finalizar_sesion(self) -> int:
        if self._inicio_sesion is None:
            return 0
        segundos = max(0, round(monotonic() - self._inicio_sesion))
        self._inicio_sesion = None
        return segundos

    def iniciar_actividad(self, titulo: str, categoria: str) -> None:
        self._actividad = ActividadEnCurso(titulo, categoria, monotonic())

    def actividad_actual(self) -> Optional[ActividadEnCurso]:
        return self._actividad

    def finalizar_actividad(self, titulo: str) -> int:
        if not self._actividad or self._actividad.titulo != titulo:
            return 0
        segundos = max(0, round(monotonic() - self._actividad.inicio))
        self._actividad = None
        return segundos
