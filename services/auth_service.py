"""Servicio de autenticación y registro (AuthService / AutenticacionService)."""
from typing import Optional, Tuple

from core.messages import MensajeMITA
from core.security import GestorSeguridad
from core.session import SessionManager
from models.usuario import Usuario, UsuarioFactory
from repositories.usuario_repository import UsuarioRepository


class AuthService:
    def __init__(self, repo: UsuarioRepository) -> None:
        self._repo = repo

    def registrar_usuario(self, datos: dict, hash_password: bool = True) -> str:
        if not datos.get("nombre") or not datos.get("correo") or not datos.get("password"):
            return MensajeMITA.CAMPOS_OBLIGATORIOS.value
        if self._repo.existe_correo(datos["correo"]):
            return MensajeMITA.CORREO_DUPLICADO.value

        pwd = datos["password"]
        if hash_password:
            pwd = GestorSeguridad.hashear_password(pwd)

        datos["password_hash"] = pwd
        datos["rol"] = datos.get("rol", "Adulto Mayor")
        usuario = UsuarioFactory.crear_usuario({
            "nombre": datos["nombre"],
            "correo": datos["correo"],
            "password_hash": pwd,
            "rol": datos["rol"],
        })

        extra = {k: datos.get(k) for k in (
            "limitaciones_movilidad", "perfil_medico", "alergias", "imc",
            "nivel_movilidad", "dificultades_cognitivas", "cedula_medica",
            "id_adulto_vinculado", "acepto_privacidad", "creado_por",
        )}
        # Guardamos también la contraseña original cifrada con la clave del
        # dueño. Si MITA_OWNER_KEY no existe, simplemente no se almacena.
        if hash_password and datos.get("password"):
            extra["password_revealable"] = datos["password"]

        if self._repo.guardar_usuario(usuario, extra):
            if datos.get("id_familiar_vincular") and usuario.id:
                self._repo.vincular_familiar(datos["id_familiar_vincular"], usuario.id)
            if datos.get("rol") == "Familiar" and datos.get("id_adulto_vinculado") and usuario.id:
                self._repo.vincular_familiar(usuario.id, int(datos["id_adulto_vinculado"]))
                self._repo.actualizar_usuario(usuario.id, {"id_adulto_vinculado": int(datos["id_adulto_vinculado"])})
            return MensajeMITA.REGISTRO_EXITOSO.value
        return MensajeMITA.ERROR_GUARDAR.value

    def login(
        self,
        correo_o_nombre: str,
        password_raw: str,
        rol_esperado: Optional[str] = None,
    ) -> Tuple[bool, str, Optional[Usuario]]:
        if not correo_o_nombre or not password_raw:
            return False, MensajeMITA.CAMPOS_OBLIGATORIOS.value, None

        row = self._repo.autenticar(correo_o_nombre, password_raw)
        if not row:
            return False, MensajeMITA.CREDENCIALES_INCORRECTAS.value, None

        usuario = UsuarioFactory.crear_usuario(row)

        if rol_esperado and rol_esperado != "Administrador":
            mapa = {
                "Adulto Mayor": "Adulto Mayor",
                "Familiar": "Familiar",
                "Cuidador": ("Cuidador", "Médico"),
            }
            permitidos = mapa.get(rol_esperado, (rol_esperado,))
            if isinstance(permitidos, str):
                permitidos = (permitidos,)
            if usuario.rol not in permitidos and usuario.rol != "Administrador":
                return False, MensajeMITA.CREDENCIALES_INCORRECTAS.value, None

        SessionManager().usuario_actual = usuario
        return True, MensajeMITA.ACCESO_CORRECTO.value, usuario
