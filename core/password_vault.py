"""Cifrado reversible de contraseñas para el "modo dueño".

PBKDF2 sólo permite verificar, no recuperar la contraseña original. Para que el
dueño del sistema pueda ver (y revocar) las contraseñas reales de los usuarios
guardamos, además del hash, una copia cifrada con **Fernet** (AES-128-CBC +
HMAC SHA-256) cuya clave vive en la variable de entorno ``MITA_OWNER_KEY`` y
nunca se almacena en la base de datos.

Si ``MITA_OWNER_KEY`` no está definida, el sistema sigue funcionando con
normalidad (login, registro) pero el descifrado queda deshabilitado.
"""
from __future__ import annotations

import base64
import hashlib
import os
from typing import Optional

try:
    from cryptography.fernet import Fernet, InvalidToken
except ImportError:  # La app puede funcionar sin la bóveda; sólo se desactiva.
    Fernet = None
    InvalidToken = Exception


_ENV_KEY = "MITA_OWNER_KEY"


class PasswordVault:
    """Cifra y descifra contraseñas con una clave que sólo conoce el dueño."""

    @staticmethod
    def _clave_desde_env() -> Optional[bytes]:
        """Deriva una clave Fernet válida a partir de ``MITA_OWNER_KEY``.

        El dueño puede definir la variable como una cadena cualquiera (no tiene
        que ser base64). Usamos SHA-256 → base64-url-32, que es exactamente el
        formato que Fernet espera.
        """
        if Fernet is None:
            return None
        material = os.getenv(_ENV_KEY)
        if not material:
            return None
        digest = hashlib.sha256(material.encode("utf-8")).digest()
        return base64.urlsafe_b64encode(digest)

    @staticmethod
    def disponible() -> bool:
        return PasswordVault._clave_desde_env() is not None

    @staticmethod
    def cifrar(password_plano: str) -> Optional[bytes]:
        clave = PasswordVault._clave_desde_env()
        if not clave or not password_plano:
            return None
        return Fernet(clave).encrypt(password_plano.encode("utf-8"))

    @staticmethod
    def descifrar(token: Optional[bytes]) -> Optional[str]:
        clave = PasswordVault._clave_desde_env()
        if not clave or not token:
            return None
        try:
            return Fernet(clave).decrypt(bytes(token)).decode("utf-8")
        except (InvalidToken, ValueError):
            return None
