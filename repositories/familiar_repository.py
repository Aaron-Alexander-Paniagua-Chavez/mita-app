"""Repositorio para familiares y relaciones familiares."""
from __future__ import annotations

from typing import List, Dict, Optional
from core.database import DatabaseManager


class FamiliarRepository:
    def __init__(self, db: DatabaseManager) -> None:
        self._db = db

    def _get_familiar_id(self, id_usuario: int) -> Optional[int]:
        """Get the familiar record id for a given usuario id, creating it if necessary."""
        existing = self._db.ejecutar_mysql(
            "SELECT id FROM familiar WHERE id_usuario = %s",
            (id_usuario,)
        )
        if existing:
            return existing[0]['id']
        # Create the familiar record
        self._db.ejecutar_mysql(
            "INSERT INTO familiar (id_usuario) VALUES (%s)",
            (id_usuario,)
        )
        # Get the newly inserted id
        nuevo = self._db.ejecutar_mysql(
            "SELECT id FROM familiar WHERE id_usuario = %s ORDER BY id DESC LIMIT 1",
            (id_usuario,)
        )
        return nuevo[0]['id'] if nuevo else None

    def crear_familiar(
        self, id_familiar: int, id_adulto: int, parentesco: str = "Familiar"
    ) -> bool:
        """Crea una relación familiar entre un familiar y un adulto mayor."""
        # Get the familiar table id for the usuario
        familiar_id = self._get_familiar_id(id_familiar)
        if familiar_id is None:
            return False
        return self._db.ejecutar_mysql(
            """INSERT INTO relaciones_familiar (id_familiar, id_adulto, tipo_relacion)
               VALUES (%s, %s, %s)""",
            (familiar_id, id_adulto, parentesco),
        ) is not None

    def obtener_familiares_de_adulto(self, id_adulto: int) -> List[Dict]:
        """Obtiene los familiares asociados a un adulto mayor."""
        return self._db.ejecutar_mysql(
            """SELECT rf.*, u.nombre AS nombre_familiar, u.correo
               FROM relaciones_familiar rf
               JOIN usuarios u ON rf.id_familiar = u.id
               WHERE rf.id_adulto = %s
               ORDER BY rf.fecha_vinculo DESC""",
            (id_adulto,),
        ) or []

    def eliminar_familiar(self, id_familiar: int, id_adulto: int) -> bool:
        """Elimina la relación familiar."""
        # Get the familiar table id for the usuario
        familiar_id = self._get_familiar_id(id_familiar)
        if familiar_id is None:
            return False
        return self._db.ejecutar_mysql(
            "DELETE FROM relaciones_familiar WHERE id_familiar = %s AND id_adulto = %s",
            (familiar_id, id_adulto),
        ) is not None