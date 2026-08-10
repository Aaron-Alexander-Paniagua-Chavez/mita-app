"""Acceso a medicamentos, tratamientos y registros de toma."""
from __future__ import annotations

from core.database import DatabaseManager


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
