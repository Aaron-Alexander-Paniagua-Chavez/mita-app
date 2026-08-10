"""Hash de contraseñas y utilidades de acceso."""
from __future__ import annotations

import base64
import hashlib
import hmac
import os


class GestorSeguridad:
    """Protege contraseñas nuevas y conserva acceso a datos históricos."""

    _ITERACIONES = 310_000
    _PREFIJO = "pbkdf2_sha256"

    @classmethod
    def hashear_password(cls, password: str) -> str:
        """Devuelve un hash PBKDF2 con sal única para cada contraseña."""
        sal = os.urandom(16)
        derivado = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), sal, cls._ITERACIONES
        )
        return "$".join((
            cls._PREFIJO,
            str(cls._ITERACIONES),
            base64.b64encode(sal).decode("ascii"),
            base64.b64encode(derivado).decode("ascii"),
        ))

    @classmethod
    def verificar_password(cls, password_raw: str, almacenado: str) -> bool:
        """Verifica PBKDF2 y admite hashes SHA-256/texto sólo para migración."""
        if not almacenado:
            return False
        if almacenado.startswith(f"{cls._PREFIJO}$"):
            try:
                _, iteraciones, sal_b64, hash_b64 = almacenado.split("$", 3)
                derivado = hashlib.pbkdf2_hmac(
                    "sha256",
                    password_raw.encode("utf-8"),
                    base64.b64decode(sal_b64),
                    int(iteraciones),
                )
                return hmac.compare_digest(
                    base64.b64encode(derivado).decode("ascii"), hash_b64
                )
            except (ValueError, TypeError):
                return False

        # Compatibilidad transitoria con el proyecto anterior. Los repositorios
        # actualizan el registro a PBKDF2 después de un inicio de sesión válido.
        hash_legacy = hashlib.sha256(password_raw.encode("utf-8")).hexdigest()
        return hmac.compare_digest(almacenado, password_raw) or hmac.compare_digest(
            almacenado, hash_legacy
        )

    @classmethod
    def requiere_actualizacion_hash(cls, almacenado: str) -> bool:
        return not almacenado.startswith(f"{cls._PREFIJO}$")

    @staticmethod
    def enmascarar_dato_sensible(valor: str) -> str:
        """Oculta información sensible para el panel de administrador."""
        if not valor or len(valor) < 4:
            return "****"
        return valor[:2] + "****" + valor[-2:]
