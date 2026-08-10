"""Gestor central de sesión (Singleton)."""
from typing import Optional

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

    def cerrar_sesion(self) -> None:
        self._usuario_actual = None
        self._rol_entrada = None

    def hay_sesion(self) -> bool:
        return self._usuario_actual is not None
