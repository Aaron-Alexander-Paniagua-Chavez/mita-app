"""Persistencia local de tiempos de uso; Mongo sólo complementa esta información."""
from __future__ import annotations

from datetime import datetime

from core.database import DatabaseManager


class RegistroUsoRepository:
    def __init__(self, db: DatabaseManager) -> None:
        self._db = db

    def registrar_sesion(self, usuario_id: int, inicio: datetime, duracion_segundos: int) -> bool:
        fin = datetime.now()
        return self._db.ejecutar_mysql(
            """INSERT INTO sesiones_uso (id_usuario, inicio, fin, duracion_segundos)
               VALUES (%s, %s, %s, %s)""",
            (usuario_id, inicio, fin, max(0, duracion_segundos)),
        ) is not None

    def registrar_actividad(
        self, usuario_id: int, titulo: str, categoria: str, duracion_segundos: int
    ) -> bool:
        return self._db.ejecutar_mysql(
            """INSERT INTO tiempos_actividad
               (id_usuario, titulo, categoria, duracion_segundos)
               VALUES (%s, %s, %s, %s)""",
            (usuario_id, titulo, categoria, max(0, duracion_segundos)),
        ) is not None

    def resumen(self, usuario_id: int) -> dict[str, int]:
        sesiones = self._db.ejecutar_mysql(
            "SELECT COALESCE(SUM(duracion_segundos), 0) AS total FROM sesiones_uso WHERE id_usuario = %s",
            (usuario_id,),
        ) or [{}]
        actividades = self._db.ejecutar_mysql(
            "SELECT COALESCE(SUM(duracion_segundos), 0) AS total FROM tiempos_actividad WHERE id_usuario = %s",
            (usuario_id,),
        ) or [{}]
        return {
            "app_segundos": int(sesiones[0].get("total", 0) or 0),
            "actividad_segundos": int(actividades[0].get("total", 0) or 0),
        }
