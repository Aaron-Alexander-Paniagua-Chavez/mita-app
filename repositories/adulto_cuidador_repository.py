"""Repositorio para la relación entre adultos mayores y cuidadores."""
from __future__ import annotations

from typing import List, Dict, Optional
from core.database import DatabaseManager


class AdultoCuidadorRepository:
    def __init__(self, db: DatabaseManager) -> None:
        self._db = db

    def vincular(
        self, id_adulto: int, id_cuidador: int, observaciones: Optional[str] = None
    ) -> bool:
        """Crea un vínculo entre un adulto mayor y un cuidador."""
        return self._db.ejecutar_mysql(
            """INSERT INTO adulto_cuidador (id_adulto, id_cuidador, observaciones)
               VALUES (%s, %s, %s)""",
            (id_adulto, id_cuidador, observaciones),
        ) is not None

    def obtener_cuidadores_de_adulto(self, id_adulto: int) -> List[Dict]:
        """Obtiene los cuidadores vinculados a un adulto mayor."""
        return self._db.ejecutar_mysql(
            """SELECT ac.*, u.nombre AS nombre_cuidador, u.correo, tc.nombre AS tipo_cuidador
               FROM adulto_cuidador ac
               JOIN cuidador c ON ac.id_cuidador = c.id
               JOIN usuarios u ON c.id_usuario = u.id
               LEFT JOIN tipo_cuidador tc ON c.id_tipo_cuidador = tc.id_tipo_cuidador
               WHERE ac.id_adulto = %s AND ac.activo = 1
               ORDER BY ac.fecha_vinculo DESC""",
            (id_adulto,),
        ) or []

    def obtener_adultos_de_cuidador(self, id_cuidador: int) -> List[Dict]:
        """Obtiene los adultos mayores vinculados a un cuidador."""
        return self._db.ejecutar_mysql(
            """SELECT ac.*, u.nombre AS nombre_adulto
               FROM adulto_cuidador ac
               JOIN adulto_mayor am ON ac.id_adulto = am.id
               JOIN usuarios u ON am.id_usuario = u.id
               WHERE ac.id_cuidador = %s AND ac.activo = 1
               ORDER BY ac.fecha_vinculo DESC""",
            (id_cuidador,),
        ) or []

    def desvincular(self, id_adulto: int, id_cuidador: int) -> bool:
        """Desvincula un adulto mayor y un cuidador (marca como inactivo)."""
        return self._db.ejecutar_mysql(
            """UPDATE adulto_cuidador
               SET activo = 0
               WHERE id_adulto = %s AND id_cuidador = %s""",
            (id_adulto, id_cuidador),
        ) is not None