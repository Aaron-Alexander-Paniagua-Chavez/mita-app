"""Gestión segura de perfiles y derecho de supresión de datos."""
from __future__ import annotations

from core.database import DatabaseManager
from core.messages import MensajeMITA
from core.security import GestorSeguridad
from repositories.usuario_repository import UsuarioRepository


class ServicioCuenta:
    """Autoriza cambios de cuenta para la propia persona, médico o administrador."""

    def __init__(self, repo: UsuarioRepository, db: DatabaseManager) -> None:
        self._repo = repo
        self._db = db

    def actualizar(self, actor, objetivo_id: int, campos: dict) -> str:
        if not actor or not actor.id:
            return MensajeMITA.SIN_AUTORIZACION.value
        es_propio = actor.id == objetivo_id
        es_personal_salud = actor.rol in {"Cuidador", "Administrador"}
        if not es_propio and not es_personal_salud:
            return MensajeMITA.SIN_AUTORIZACION.value
        campos = dict(campos)
        # Los cambios de rol implican crear o retirar perfiles relacionales;
        # por ello no pertenecen al formulario de datos personales.
        campos.pop("rol", None)
        if es_propio:
            permitidos = {"nombre", "correo", "password", "genero", "telefono", "ubicacion", "foto_perfil"}
            if actor.rol == "Adulto Mayor":
                permitidos |= {
                    "descripcion_movilidad", "perfil_medico", "descripcion_habitos", "alergias",
                    "imc", "dificultades_cognitivas", "dieta", "sueno", "antecedentes_medicos"
                }
            elif actor.rol in ("Cuidador", "Médico"):
                permitidos |= {"cedula_medica", "especialidad", "tipo_cuidador"}
            campos = {clave: valor for clave, valor in campos.items() if clave in permitidos}
        if campos.get("password"):
            campos["password_hash"] = GestorSeguridad.hashear_password(campos.pop("password"))
        else:
            campos.pop("password", None)
        if self._repo.actualizar_usuario(objetivo_id, campos):
            return MensajeMITA.USUARIO_ACTUALIZADO.value
        return MensajeMITA.ERROR_GUARDAR.value

    def eliminar_cuenta_propia(self, actor) -> str:
        if not actor or not actor.id:
            return MensajeMITA.SIN_AUTORIZACION.value
        user_id = actor.id
        if not self._repo.eliminar_usuario(user_id):
            return MensajeMITA.ERROR_GUARDAR.value
        # La información transaccional se elimina por ON DELETE CASCADE;
        # MongoDB requiere este paso explícito porque es otra base de datos.
        self._db.eliminar_datos_mongo_usuario(user_id)
        return MensajeMITA.USUARIO_ELIMINADO.value
