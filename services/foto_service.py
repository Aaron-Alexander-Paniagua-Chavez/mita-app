"""Servicio para actualizar o eliminar la foto de perfil en DB tras guardarla localmente."""
from core.messages import MensajeMITA
from repositories.foto_repository import FotoRepository
from repositories.usuario_repository import UsuarioRepository


class FotoService:
    def __init__(self, foto_repo: FotoRepository, usuario_repo: UsuarioRepository):
        self._foto_repo = foto_repo
        self._usuario_repo = usuario_repo

    def actualizar_foto_perfil(self, user_id: int, ruta_origen: str) -> tuple[bool, str]:
        usuario = self._usuario_repo.obtener_por_id(user_id)
        if not usuario:
            return False, MensajeMITA.USUARIO_NO_ENCONTRADO.value

        foto_anterior = usuario.get("foto_perfil")

        exito, resultado = self._foto_repo.guardar_foto(ruta_origen, user_id)
        if not exito:
            return False, resultado

        if self._usuario_repo.actualizar_usuario(user_id, {"foto_perfil": resultado}):
            if foto_anterior:
                self._foto_repo.eliminar_foto(foto_anterior)
            return True, MensajeMITA.USUARIO_ACTUALIZADO.value

        self._foto_repo.eliminar_foto(resultado)
        return False, MensajeMITA.ERROR_GUARDAR.value

    def eliminar_foto_perfil(self, user_id: int) -> tuple[bool, str]:
        usuario = self._usuario_repo.obtener_por_id(user_id)
        if not usuario:
            return False, MensajeMITA.USUARIO_NO_ENCONTRADO.value

        foto_actual = usuario.get("foto_perfil")
        if foto_actual:
            self._foto_repo.eliminar_foto(foto_actual)
            self._usuario_repo.actualizar_usuario(user_id, {"foto_perfil": None})

        return True, "Foto de perfil eliminada."
