"""Servicios de comunidad y permisos de seguimiento."""
from typing import Optional, Tuple

from core.messages import MensajeMITA
from models.progreso import GestorProgreso, ReporteCuidador, ReporteFamiliar
from models.usuario import Usuario
from repositories.comunidad_repository import ComunidadRepository
from repositories.progreso_repository import ProgresoRepository
from repositories.usuario_repository import UsuarioRepository


class PermisoSeguimiento:
    def __init__(self, repo: UsuarioRepository) -> None:
        self._repo = repo

    def verificar_familiar(self, id_familiar: int, id_adulto: int) -> bool:
        return self._repo.familiar_autorizado(id_familiar, id_adulto)

    def obtener_resumen_familiar(
        self,
        id_familiar: int,
        id_adulto: int,
        progreso_repo: ProgresoRepository,
    ) -> Tuple[Optional[str], str]:
        if not self.verificar_familiar(id_familiar, id_adulto):
            adulto = self._repo.obtener_por_id(id_adulto)
            familiar = self._repo.obtener_por_id(id_familiar)
            if not adulto or not familiar:
                return None, MensajeMITA.SIN_AUTORIZACION.value
            if familiar.get("id_adulto_vinculado") != id_adulto:
                return None, MensajeMITA.SIN_AUTORIZACION.value

        adulto_data = self._repo.obtener_por_id(id_adulto)
        if not adulto_data:
            return None, MensajeMITA.SIN_AUTORIZACION.value

        usuario = UsuarioRepository.dict_a_usuario(adulto_data)
        progreso = GestorProgreso()
        progreso.cargar_desde_db(progreso_repo.obtener_progreso(id_adulto))
        reporte = ReporteFamiliar()
        return reporte.generar_resumen(usuario, progreso), MensajeMITA.INFO_FAMILIAR.value


class ComunidadService:
    def __init__(self, repo: ComunidadRepository) -> None:
        self._repo = repo

    def obtener_publicaciones(self):
        return self._repo.obtener_publicaciones()

    def enviar_mensaje(self, id_autor: int, nombre: str, texto: str) -> str:
        return self._repo.enviar_publicacion(id_autor, nombre, texto)
