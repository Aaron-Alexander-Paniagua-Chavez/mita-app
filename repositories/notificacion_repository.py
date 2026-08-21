"""Repositorio para notificaciones y recordatorios de medicamentos."""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from core.database import DatabaseManager


class NotificacionRepository:
    def __init__(self, db: DatabaseManager) -> None:
        self._db = db

    def crear_notificacion(
        self,
        id_usuario: int,
        mensaje: str,
        fecha_programada: datetime,
        tipo: str = "Medicamento",
        id_registro_toma: Optional[int] = None,
    ) -> bool:
        return self._db.ejecutar_mysql(
            """INSERT INTO notificacion (id_usuario, id_registro_toma, tipo, mensaje, fecha_programada, estado)
               VALUES (%s, %s, %s, %s, %s, 'Pendiente')""",
            (id_usuario, id_registro_toma, tipo, mensaje, fecha_programada),
        ) is not None

    def obtener_pendientes_usuario(self, id_usuario: int) -> list[dict]:
        return self._db.ejecutar_mysql(
            """SELECT * FROM notificacion 
               WHERE id_usuario = %s AND estado = 'Pendiente' AND fecha_programada <= NOW()
               ORDER BY fecha_programada ASC""",
            (id_usuario,),
        ) or []

    def marcar_enviada(self, id_notificacion: int) -> bool:
        return self._db.ejecutar_mysql(
            "UPDATE notificacion SET estado = 'Enviado', fecha_enviada = NOW() WHERE id = %s",
            (id_notificacion,),
        ) is not None

    def marcar_leida(self, id_notificacion: int) -> bool:
        return self._db.ejecutar_mysql(
            "UPDATE notificacion SET estado = 'Leido' WHERE id = %s",
            (id_notificacion,),
        ) is not None
