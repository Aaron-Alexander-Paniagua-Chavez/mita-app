"""Modelo de usuarios — POO, herencia, encapsulamiento (Bloques 1–3)."""
from abc import ABC, abstractmethod
from typing import Optional


class Usuario(ABC):
    """Clase base abstracta con atributos protegidos y propiedades."""

    def __init__(
        self,
        nombre: str,
        correo: str,
        password_hash: str,
        rol: str,
        user_id: Optional[int] = None,
    ) -> None:
        self._id = user_id
        self._nombre = nombre
        self._correo = correo
        self._password_hash = password_hash
        self._rol = rol

    @property
    def id(self) -> Optional[int]:
        return self._id

    @id.setter
    def id(self, val: int) -> None:
        self._id = val

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def correo(self) -> str:
        return self._correo

    @property
    def password_hash(self) -> str:
        return self._password_hash

    @property
    def rol(self) -> str:
        return self._rol

    @abstractmethod
    def panel_destino(self) -> str:
        """Ruta del panel según rol (polimorfismo)."""


class AdultoMayor(Usuario):
    """Adulto mayor con perfil médico encapsulado."""

    def __init__(
        self,
        nombre: str,
        correo: str,
        password_hash: str,
        limitaciones: str = "Ninguna",
        perfil_medico: str = "Condición estable",
        alergias: str = "Ninguna",
        imc: float = 22.0,
        nivel_movilidad: str = "Normal",
        dificultades_cognitivas: str = "Ninguna",
        user_id: Optional[int] = None,
    ) -> None:
        super().__init__(nombre, correo, password_hash, "Adulto Mayor", user_id)
        self._limitaciones_movilidad = limitaciones
        self._perfil_medico = perfil_medico
        self._alergias = alergias
        self._imc = imc
        self._nivel_movilidad = nivel_movilidad
        self._dificultades_cognitivas = dificultades_cognitivas

    @property
    def limitaciones_movilidad(self) -> str:
        return self._limitaciones_movilidad

    @limitaciones_movilidad.setter
    def limitaciones_movilidad(self, val: str) -> None:
        if not val.strip():
            raise ValueError("Las limitaciones no pueden estar vacías")
        self._limitaciones_movilidad = val

    @property
    def perfil_medico(self) -> str:
        return self._perfil_medico

    @property
    def alergias(self) -> str:
        return self._alergias

    @property
    def imc(self) -> float:
        return self._imc

    @imc.setter
    def imc(self, val: float) -> None:
        if val <= 0 or val > 80:
            raise ValueError("IMC fuera de rango válido")
        self._imc = val

    @property
    def nivel_movilidad(self) -> str:
        return self._nivel_movilidad

    @property
    def dificultades_cognitivas(self) -> str:
        return self._dificultades_cognitivas

    def panel_destino(self) -> str:
        return "adulto"


class Familiar(Usuario):
    """Familiar o encargado vinculado a un adulto mayor."""

    def __init__(
        self,
        nombre: str,
        correo: str,
        password_hash: str,
        id_adulto_vinculado: Optional[int] = None,
        user_id: Optional[int] = None,
    ) -> None:
        super().__init__(nombre, correo, password_hash, "Familiar", user_id)
        self._id_adulto_vinculado = id_adulto_vinculado

    @property
    def id_adulto_vinculado(self) -> Optional[int]:
        return self._id_adulto_vinculado

    def panel_destino(self) -> str:
        return "familiar"


class Cuidador(Usuario):
    """Personal médico o de cuidado."""

    def __init__(
        self,
        nombre: str,
        correo: str,
        password_hash: str,
        cedula_medica: str = "MED-0000",
        user_id: Optional[int] = None,
    ) -> None:
        super().__init__(nombre, correo, password_hash, "Cuidador", user_id)
        self._cedula_medica = cedula_medica

    @property
    def cedula_medica(self) -> str:
        return self._cedula_medica

    def panel_destino(self) -> str:
        return "cuidador"


class Administrador(Usuario):
    """Superusuario para mantenimiento del sistema."""

    def __init__(
        self,
        nombre: str,
        correo: str,
        password_hash: str,
        user_id: Optional[int] = None,
    ) -> None:
        super().__init__(nombre, correo, password_hash, "Administrador", user_id)

    def panel_destino(self) -> str:
        return "admin"


class UsuarioFactory:
    """Fábrica para instanciar usuarios según rol (OCP)."""

    @staticmethod
    def crear_usuario(datos: dict) -> Usuario:
        rol = datos.get("rol", "Adulto Mayor")
        pwd = datos.get("contraseña") or datos.get("password_hash") or datos.get("password", "")
        uid = datos.get("id")
        nombre = datos["nombre"]
        correo = datos["correo"]

        if rol == "Adulto Mayor":
            return AdultoMayor(
                nombre, correo, pwd,
                limitaciones=datos.get("limitaciones_movilidad", "Ninguna"),
                perfil_medico=datos.get("perfil_medico", "Condición estable"),
                alergias=datos.get("alergias", "Ninguna"),
                imc=float(datos.get("imc", 22.0)),
                nivel_movilidad=datos.get("nivel_movilidad", "Normal"),
                dificultades_cognitivas=datos.get("dificultades_cognitivas", "Ninguna"),
                user_id=uid,
            )
        if rol == "Familiar":
            return Familiar(
                nombre, correo, pwd,
                id_adulto_vinculado=datos.get("id_adulto_vinculado"),
                user_id=uid,
            )
        if rol in ("Cuidador", "Médico"):
            return Cuidador(
                nombre, correo, pwd,
                cedula_medica=datos.get("cedula_medica", "MED-0000"),
                user_id=uid,
            )
        if rol == "Administrador":
            return Administrador(nombre, correo, pwd, user_id=uid)
        return AdultoMayor(nombre, correo, pwd, user_id=uid)
