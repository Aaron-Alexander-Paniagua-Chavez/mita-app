"""Servicio para la gestión de dietas y registros de sueño de adultos mayores."""
from datetime import date
from typing import List, Optional

from repositories.dieta_sueno_repository import DietaSuenoRepository
from repositories.usuario_repository import UsuarioRepository


class DietaSuenoService:
    def __init__(self, repo: DietaSuenoRepository, usuario_repo: UsuarioRepository):
        self._repo = repo
        self._usuario_repo = usuario_repo

    def _obtener_id_adulto(self, id_usuario: int) -> Optional[int]:
        usuario = self._usuario_repo.obtener_por_id(id_usuario)
        if not usuario or usuario["rol"] != "Adulto Mayor":
            return None
        # Buscar ID en adulto_mayor
        rows = self._usuario_repo._db.ejecutar_mysql(
            "SELECT id FROM adulto_mayor WHERE id_usuario = %s", (id_usuario,)
        )
        return rows[0]["id"] if rows else None

    # Dieta
    def registrar_dieta(self, id_usuario: int, tipo_dieta: str, descripcion: str) -> tuple[bool, str]:
        id_adulto = self._obtener_id_adulto(id_usuario)
        if not id_adulto:
            return False, "Adulto mayor no encontrado."
        if not tipo_dieta or not descripcion:
            return False, "Tipo de dieta y descripción son obligatorios."
        ok = self._repo.registrar_dieta(id_adulto, tipo_dieta, descripcion)
        return ok, "Dieta registrada correctamente." if ok else "Error al registrar dieta."

    def listar_dietas(self, id_usuario: int) -> list[dict]:
        id_adulto = self._obtener_id_adulto(id_usuario)
        if not id_adulto:
            return []
        return self._repo.obtener_dietas_adulto(id_adulto)

    def eliminar_dieta(self, id_dieta: int) -> tuple[bool, str]:
        ok = self._repo.eliminar_dieta(id_dieta)
        return ok, "Dieta eliminada." if ok else "Error al eliminar dieta."

    # Sueño
    def registrar_sueno(
        self,
        id_usuario: int,
        fecha: date,
        duracion_minutos: int,
        calidad: str = "Buena",
        observaciones: str = "",
    ) -> tuple[bool, str]:
        id_adulto = self._obtener_id_adulto(id_usuario)
        if not id_adulto:
            return False, "Adulto mayor no encontrado."
        if duracion_minutos <= 0 or duracion_minutos > 1440:
            return False, "La duración del sueño debe ser válida (entre 1 minuto y 24 horas)."
        ok = self._repo.registrar_sueno(
            id_adulto=id_adulto,
            fecha=fecha,
            duracion_minutos=duracion_minutos,
            calidad=calidad,
            observaciones=observaciones,
        )
        return ok, "Registro de sueño guardado." if ok else "Error al registrar sueño."

    def listar_sueno(self, id_usuario: int) -> list[dict]:
        id_adulto = self._obtener_id_adulto(id_usuario)
        if not id_adulto:
            return []
        return self._repo.obtener_registros_sueno(id_adulto)

    def eliminar_sueno(self, id_sueno: int) -> tuple[bool, str]:
        ok = self._repo.eliminar_sueno(id_sueno)
        return ok, "Registro de sueño eliminado." if ok else "Error al eliminar registro."
