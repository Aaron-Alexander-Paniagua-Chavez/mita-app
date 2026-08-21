"""Repositorio para gestión de dieta_adulto y registro_sueno en MySQL."""
from __future__ import annotations

from datetime import date, time
from typing import List, Optional

from core.database import DatabaseManager


class DietaSuenoRepository:
    def __init__(self, db: DatabaseManager) -> None:
        self._db = db

    # ------------------------------------------------------------------
    # DIETA
    # ------------------------------------------------------------------
    def registrar_dieta(
        self,
        id_adulto: int,
        tipo_dieta: str,
        descripcion: str,
        fecha_inicio: Optional[date] = None,
        fecha_fin: Optional[date] = None,
    ) -> bool:
        return self._db.ejecutar_mysql(
            """INSERT INTO dieta_adulto (id_adulto, tipo_dieta, descripcion, fecha_inicio, fecha_fin, activa)
               VALUES (%s, %s, %s, %s, %s, 1)""",
            (id_adulto, tipo_dieta, descripcion, fecha_inicio or date.today(), fecha_fin),
        ) is not None

    def obtener_dietas_adulto(self, id_adulto: int) -> list[dict]:
        return self._db.ejecutar_mysql(
            "SELECT * FROM dieta_adulto WHERE id_adulto = %s ORDER BY id DESC", (id_adulto,)
        ) or []

    def actualizar_dieta(self, id_dieta: int, tipo_dieta: str, descripcion: str, activa: bool = True) -> bool:
        return self._db.ejecutar_mysql(
            "UPDATE dieta_adulto SET tipo_dieta = %s, descripcion = %s, activa = %s WHERE id = %s",
            (tipo_dieta, descripcion, 1 if activa else 0, id_dieta),
        ) is not None

    def eliminar_dieta(self, id_dieta: int) -> bool:
        return self._db.ejecutar_mysql("DELETE FROM dieta_adulto WHERE id = %s", (id_dieta,)) is not None

    # ------------------------------------------------------------------
    # SUEÑO
    # ------------------------------------------------------------------
    def registrar_sueno(
        self,
        id_adulto: int,
        fecha: date,
        hora_inicio: Optional[str] = None,
        hora_fin: Optional[str] = None,
        duracion_minutos: Optional[int] = None,
        calidad: str = "Buena",
        observaciones: Optional[str] = None,
    ) -> bool:
        return self._db.ejecutar_mysql(
            """INSERT INTO registro_sueno (id_adulto, fecha, hora_inicio, hora_fin, duracion_minutos, calidad, observaciones)
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (id_adulto, fecha, hora_inicio, hora_fin, duracion_minutos, calidad, observaciones),
        ) is not None

    def obtener_registros_sueno(self, id_adulto: int, limite: int = 30) -> list[dict]:
        return self._db.ejecutar_mysql(
            "SELECT * FROM registro_sueno WHERE id_adulto = %s ORDER BY fecha DESC LIMIT %s",
            (id_adulto, limite),
        ) or []

    def actualizar_sueno(
        self,
        id_sueno: int,
        duracion_minutos: int,
        calidad: str,
        observaciones: Optional[str] = None,
    ) -> bool:
        return self._db.ejecutar_mysql(
            "UPDATE registro_sueno SET duracion_minutos = %s, calidad = %s, observaciones = %s WHERE id = %s",
            (duracion_minutos, calidad, observaciones, id_sueno),
        ) is not None

    def eliminar_sueno(self, id_sueno: int) -> bool:
        return self._db.ejecutar_mysql("DELETE FROM registro_sueno WHERE id = %s", (id_sueno,)) is not None
