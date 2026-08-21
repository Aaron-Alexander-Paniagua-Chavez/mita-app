"""Gestor central de sesión y restauración local explícita."""
from __future__ import annotations

import json
from typing import Optional

from config.settings import SESSION_SETTINGS_PATH
from models.usuario import Usuario


class SessionManager:
    """Mantiene el usuario autenticado y el rol activo de la interfaz."""

    _instance: Optional["SessionManager"] = None

    def __new__(cls) -> "SessionManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._usuario_actual = None
            cls._instance._rol_entrada = None
        return cls._instance

    @property
    def usuario_actual(self) -> Optional[Usuario]:
        return self._usuario_actual

    @usuario_actual.setter
    def usuario_actual(self, usuario: Optional[Usuario]) -> None:
        self._usuario_actual = usuario

    @property
    def rol_entrada(self) -> Optional[str]:
        return self._rol_entrada

    @rol_entrada.setter
    def rol_entrada(self, rol: Optional[str]) -> None:
        self._rol_entrada = rol

    def guardar_sesion_persistente(self, usuario: Usuario) -> None:
        """Guarda un perfil mínimo, nunca una contraseña ni su hash.

        Es una comodidad para equipos personales. Cerrar sesión elimina este
        archivo, de modo que el control permanece en manos de la persona.
        """
        if not usuario.id:
            return
        datos = {
            "id": usuario.id,
            "nombre": usuario.nombre,
            "correo": usuario.correo,
            "rol": usuario.rol,
        }
        for campo in (
            "descripcion_movilidad", "perfil_medico", "alergias", "imc",
            "dificultades_cognitivas", "cedula_medica",
            "id_adulto_vinculado",
        ):
            if hasattr(usuario, campo):
                datos[campo] = getattr(usuario, campo)
        try:
            SESSION_SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
            SESSION_SETTINGS_PATH.write_text(json.dumps(datos), encoding="utf-8")
            try:
                SESSION_SETTINGS_PATH.chmod(0o600)
            except OSError:
                pass
        except OSError:
            pass

    def restaurar_sesion(self, user_repository) -> Optional[Usuario]:
        """Restaura el usuario actual; usa caché sólo si MySQL está offline."""
        try:
            datos = json.loads(SESSION_SETTINGS_PATH.read_text(encoding="utf-8"))
            user_id = int(datos.get("id", 0))
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            return None
        if not user_id:
            return None

        actual = user_repository.obtener_por_id(user_id)
        if actual:
            usuario = user_repository.dict_a_usuario(actual)
        else:
            # Sin red/local DB, la app puede seguir mostrando contenido no clínico
            # ya cacheado. En cuanto MySQL vuelva, se refresca el perfil.
            from models.usuario import UsuarioFactory
            usuario = UsuarioFactory.crear_usuario({**datos, "password_hash": ""})
        self._usuario_actual = usuario
        return usuario

    def cerrar_sesion(self, borrar_persistida: bool = True) -> None:
        self._usuario_actual = None
        self._rol_entrada = None
        if borrar_persistida:
            try:
                SESSION_SETTINGS_PATH.unlink(missing_ok=True)
            except OSError:
                pass

    def hay_sesion(self) -> bool:
        return self._usuario_actual is not None
