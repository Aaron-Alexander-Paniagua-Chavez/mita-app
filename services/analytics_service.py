"""Casos de uso de analítica: la UI no conoce detalles de MongoDB."""
from __future__ import annotations

from typing import Any, Optional

from repositories.estadistica_repository import EstadisticaRepository


class AnalyticsService:
    def __init__(self, repository: EstadisticaRepository) -> None:
        self._repository = repository

    def registrar_login(self, usuario_id: int) -> Optional[Any]:
        self._repository.registrar_evento("login", usuario_id)
        return self._repository.iniciar_sesion(usuario_id, version_app="MITA 2.0")

    def registrar_logout(self, usuario_id: Optional[int], session_id: Any) -> None:
        self._repository.registrar_evento("logout", usuario_id)
        self._repository.cerrar_sesion(session_id)

    def registrar_cambio_pantalla(self, usuario_id: Optional[int], pantalla: str) -> None:
        self._repository.registrar_evento("cambio_pantalla", usuario_id, pantalla=pantalla)

    def registrar_resultado_actividad(
        self, usuario_id: int, actividad: str, categoria: str, **resultado: Any
    ) -> None:
        self._repository.guardar_estadistica({
            "usuario": usuario_id,
            "actividad": actividad,
            "categoria": categoria,
            **resultado,
        })
