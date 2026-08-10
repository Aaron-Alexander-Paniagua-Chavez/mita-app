"""Catálogo relacional de actividades; sus resultados viven en MongoDB."""
from __future__ import annotations

from typing import Optional

from core.database import DatabaseManager


class ActividadRepository:
    def __init__(self, db: DatabaseManager) -> None:
        self._db = db

    def listar_activas(self, tipo: Optional[str] = None) -> list[dict]:
        if not self._db.mysql_ready:
            return []
        sql = "SELECT * FROM actividad WHERE activa = 1"
        params: tuple = ()
        if tipo:
            sql += " AND tipo = %s"
            params = (tipo,)
        return self._db.ejecutar_mysql(sql + " ORDER BY nivel, nombre", params) or []

    def obtener_por_nombre(self, nombre: str, tipo: str) -> Optional[dict]:
        if not self._db.mysql_ready:
            return None
        rows = self._db.ejecutar_mysql(
            "SELECT * FROM actividad WHERE nombre = %s AND tipo = %s AND activa = 1",
            (nombre, tipo),
        )
        return rows[0] if rows else None
