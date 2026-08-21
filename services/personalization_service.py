"""Preferencias, intereses y sugerencias de motivación de MITA.

Diseño de preferencias:
    La tabla ``preferencias_usuario`` almacena **una sola columna JSON**
    (``preferencias``). No existen columnas adicionales ni tablas secundarias
    para tema, idioma, accesibilidad o tamaño de fuente. Se mantiene este
    diseño porque el JSON permite añadir o eliminar claves sin migraciones de
    esquema, adaptándose fácilmente a nuevas preferencias futuras.

    Flujo:
        ``preferencias_usuario.preferencias`` (JSON)
        → ``PreferenciasRepository.obtener / guardar``
        → ``PersonalizationService``
        → UI (app.py / role_views.py)
"""
from __future__ import annotations

from typing import Any

from repositories.preferencias_repository import PreferenciasRepository


DEFAULT_PREFERENCIAS: dict[str, Any] = {
    "tema": "clasico",
    "estilo_instrucciones": "ilustrado",
    "recordatorio_diario": False,
    "intereses": [],
    "animaciones_suaves": True,
    "mantener_sesion": True,
    "font_scale": 1.0,
    "modo_oscuro": False,
    "idioma": "es",
    "descripcion_movilidad": "",
    "dificultades_cognitivas": "",
}


class PersonalizationService:
    def __init__(self, repository: PreferenciasRepository) -> None:
        self._repository = repository

    def obtener(self, usuario_id: int) -> dict[str, Any]:
        return {**DEFAULT_PREFERENCIAS, **self._repository.obtener(usuario_id)}

    def guardar(self, usuario_id: int, cambios: dict[str, Any]) -> dict[str, Any]:
        actual = self.obtener(usuario_id)
        actual.update({k: v for k, v in cambios.items() if k in DEFAULT_PREFERENCIAS})
        self._repository.guardar(usuario_id, actual)
        return actual

    @staticmethod
    def mensaje_motivacion(preferencias: dict[str, Any], puntos: int, racha: int) -> str:
        intereses = preferencias.get("intereses") or []
        detalle = f" Piensa en {intereses[0]}." if intereses else ""
        if racha >= 3:
            return f"¡Llevas {racha} días de constancia! Cada paso cuenta.{detalle}"
        if puntos >= 40:
            return f"Ya reuniste {puntos} puntos. Hoy avanzas a tu ritmo.{detalle}"
        return f"Una actividad breve es un buen comienzo. Tú eliges el ritmo.{detalle}"
