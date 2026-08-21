"""Acceso a medicamentos, tratamientos, registros de toma y vista de adherencia."""
from __future__ import annotations

from typing import List, Dict, Tuple, Optional
from datetime import datetime, date

from core.database import DatabaseManager


MAP_ESTADO_TOMA = {
    "programado": 1,
    "tomado": 2,
    "omitido": 3,
    "atrasado": 4,
}


class MedicamentoRepository:
    def __init__(self, db: DatabaseManager) -> None:
        self._db = db

    def listar_catalogo(self) -> list[dict]:
        if not self._db.mysql_ready:
            return []
        return self._db.ejecutar_mysql(
            "SELECT * FROM medicamento ORDER BY nombre, presentacion"
        ) or []

    def tratamientos_de_adulto(self, id_usuario_adulto: int) -> list[dict]:
        if not self._db.mysql_ready:
            return []
        return self._db.ejecutar_mysql(
            """SELECT t.*, m.nombre AS medicamento, m.presentacion
               FROM tratamiento t
               JOIN adulto_mayor am ON am.id = t.id_adulto
               JOIN medicamento m ON m.id = t.id_medicamento
               WHERE am.id_usuario = %s AND t.activo = 1
               ORDER BY m.nombre""",
            (id_usuario_adulto,),
        ) or []

    def crear_tratamiento(
        self, id_adulto: int, id_medicamento: int, dosis: str, frecuencia: str,
        fecha_inicio: Optional[date] = None, fecha_fin: Optional[date] = None, id_cuidador: Optional[int] = None
    ) -> bool:
        return self._db.ejecutar_mysql(
            """INSERT INTO tratamiento (id_adulto, id_medicamento, id_cuidador, dosis, frecuencia, fecha_inicio, fecha_fin, activo)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
            (id_adulto, id_medicamento, id_cuidador, dosis, frecuencia, fecha_inicio, fecha_fin, 1)
        ) is not None

    def registrar_toma(
        self, id_tratamiento: int, estado: str, hora_programada: str = None, 
        hora_real: str = None, observaciones: str = None
    ) -> bool:
        id_estado = MAP_ESTADO_TOMA.get(estado.lower(), 1)
        return self._db.ejecutar_mysql(
            """INSERT INTO registro_toma (id_tratamiento, id_estado, hora_programada, hora_real, observaciones)
               VALUES (%s, %s, %s, %s, %s)""",
            (id_tratamiento, id_estado, hora_programada, hora_real, observaciones)
        ) is not None

    def obtener_historial_tomas(self, id_tratamiento: int) -> list[dict]:
        return self._db.ejecutar_mysql(
            """SELECT rt.*, et.nombre AS estado_nombre
               FROM registro_toma rt
               JOIN estado_toma et ON rt.id_estado = et.id_estado
               WHERE rt.id_tratamiento = %s 
               ORDER BY rt.fecha_hora DESC LIMIT 50""",
            (id_tratamiento,)
        ) or []

    def calcular_adherencia(self, id_adulto: int, fecha_desde: date, fecha_hasta: date) -> Tuple[int, int]:
        """Devuelve (tomas_completadas, tomas_totales)."""
        rows = self._db.ejecutar_mysql(
            """SELECT 
                 COUNT(*) AS total,
                 SUM(CASE WHEN rt.id_estado IN (2, 4) THEN 1 ELSE 0 END) AS completadas
               FROM registro_toma rt
               JOIN tratamiento t ON t.id = rt.id_tratamiento
               WHERE t.id_adulto = %s AND rt.fecha_hora >= %s AND rt.fecha_hora <= %s""",
            (id_adulto, fecha_desde, fecha_hasta)
        )
        if not rows:
            return 0, 0
        row = rows[0]
        return int(row.get("completadas") or 0), int(row.get("total") or 0)

    def obtener_adherencia_vista(self, id_adulto: int) -> list[dict]:
        """Consulta la vista SQL vw_adherencia_medicacion."""
        return self._db.ejecutar_mysql(
            "SELECT * FROM vw_adherencia_medicacion WHERE id_adulto = %s",
            (id_adulto,)
        ) or []

    def obtener_recordatorios_pendientes(self, id_adulto: int) -> list[dict]:
        return self._db.ejecutar_mysql(
            """SELECT t.id as id_tratamiento, t.dosis, t.frecuencia, m.nombre AS medicamento
               FROM tratamiento t
               JOIN medicamento m ON m.id = t.id_medicamento
               WHERE t.id_adulto = %s AND t.activo = 1""",
            (id_adulto,)
        ) or []
