"""Repositorio para actividades, registro_actividad y consulta de vw_progreso."""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from core.database import DatabaseManager


class ActividadRepository:
    def __init__(self, db: DatabaseManager) -> None:
        self._db = db

    def registrar_actividad(
        self,
        id_usuario: int,
        id_actividad: Optional[int],
        hora_inicio: Optional[datetime] = None,
        hora_fin: Optional[datetime] = None,
        nivel_alcanzado: Optional[int] = 1,
        desempeno: str = "Bueno",
        puntos: int = 10,
        observaciones: Optional[str] = None,
    ) -> bool:
        return self._db.ejecutar_mysql(
            """INSERT INTO registro_actividad 
               (id_usuario, id_actividad, hora_inicio, hora_fin, nivel_alcanzado, desempeno, puntos, observaciones)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
            (id_usuario, id_actividad, hora_inicio, hora_fin, nivel_alcanzado, desempeno, puntos, observaciones),
        ) is not None

    def obtener_progreso_vista(self, id_usuario: int) -> Optional[dict]:
        rows = self._db.ejecutar_mysql(
            "SELECT * FROM vw_progreso WHERE id_usuario = %s", (id_usuario,)
        )
        return rows[0] if rows else None

    def listar_actividades_usuario(self, id_usuario: int, limite: int = 50) -> list[dict]:
        return self._db.ejecutar_mysql(
            """SELECT ra.*, a.nombre AS nombre_actividad, ta.nombre AS tipo_actividad
               FROM registro_actividad ra
               LEFT JOIN actividad a ON ra.id_actividad = a.id
               LEFT JOIN tipo_actividad ta ON a.id_tipo_actividad = ta.id_tipo_actividad
               WHERE ra.id_usuario = %s
               ORDER BY ra.fecha DESC LIMIT %s""",
            (id_usuario, limite),
        ) or []
