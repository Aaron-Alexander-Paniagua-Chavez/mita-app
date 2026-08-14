"""Administrador de usuarios — CRUD con auditoría (RF01, RF07)."""
from datetime import datetime
from typing import List, Optional

from core.messages import MensajeMITA
from core.security import GestorSeguridad
from repositories.usuario_repository import UsuarioRepository
from core.database import BaseDatosService


class AdministradorUsuarios:
    def __init__(self, repo: UsuarioRepository, db: BaseDatosService) -> None:
        self._repo = repo
        self._db = db

    def _log(self, accion: str, detalle: str, id_admin: Optional[int]) -> None:
        ahora = datetime.now().isoformat()
        self._db.ejecutar_mysql(
            "INSERT INTO auditoria (accion, detalle, id_admin, fecha_hora) VALUES (%s,%s,%s,%s)",
            (accion, detalle, id_admin, ahora),
        )

    def listar_usuarios(self) -> List[dict]:
        return self._repo.listar_todos()

    def crear_usuario(self, datos: dict, id_admin: int) -> str:
        from services.auth_service import AuthService
        auth = AuthService(self._repo)
        res = auth.registrar_usuario(datos, hash_password=True)
        if res == MensajeMITA.REGISTRO_EXITOSO.value:
            self._log("CREAR_USUARIO", f"Correo: {datos.get('correo')}", id_admin)
        return res

    def modificar_usuario(self, user_id: int, campos: dict, id_admin: int) -> str:
        if "password" in campos and campos["password"]:
            plain = campos["password"]
            campos["password_hash"] = GestorSeguridad.hashear_password(plain)
        if self._repo.actualizar_usuario(user_id, campos):
            self._log("MODIFICAR_USUARIO", f"ID: {user_id}", id_admin)
            return MensajeMITA.USUARIO_ACTUALIZADO.value
        return MensajeMITA.ERROR_GUARDAR.value

    def eliminar_usuario(self, user_id: int, id_admin: int) -> str:
        if self._repo.eliminar_usuario(user_id):
            self._log("ELIMINAR_USUARIO", f"ID: {user_id}", id_admin)
            return MensajeMITA.USUARIO_ELIMINADO.value
        return MensajeMITA.ERROR_GUARDAR.value

    def consultar_usuario(self, user_id: int) -> Optional[dict]:
        return self._repo.obtener_por_id(user_id)
