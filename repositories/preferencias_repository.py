"""Persistencia de preferencias no clínicas por usuario."""
from __future__ import annotations

import json
from typing import Any

from core.database import DatabaseManager


class PreferenciasRepository:
    def __init__(self, db: DatabaseManager) -> None:
        self._db = db

    def obtener(self, usuario_id: int) -> dict[str, Any]:
        filas = self._db.ejecutar_mysql(
            "SELECT preferencias FROM preferencias_usuario WHERE id_usuario = %s",
            (usuario_id,),
        ) or []
        if not filas:
            return {}
        try:
            valor = json.loads(filas[0]["preferencias"] or "{}")
            return valor if isinstance(valor, dict) else {}
        except (KeyError, TypeError, json.JSONDecodeError):
            return {}

    def guardar(self, usuario_id: int, preferencias: dict[str, Any]) -> bool:
        serializado = json.dumps(preferencias, ensure_ascii=False)
        resultado = self._db.ejecutar_mysql(
            """INSERT INTO preferencias_usuario (id_usuario, preferencias)
               VALUES (%s, %s)
               ON DUPLICATE KEY UPDATE preferencias = VALUES(preferencias),
               actualizado_en = CURRENT_TIMESTAMP""",
            (usuario_id, serializado),
        )
        return resultado is not None
