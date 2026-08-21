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
        genero: Optional[str] = None,
        telefono: Optional[str] = None,
        ubicacion: Optional[str] = None,
        foto_perfil: Optional[str] = None,
        user_id: Optional[int] = None,
    ) -> None:
        self._id = user_id
        self._nombre = nombre
        self._correo = correo
        self._password_hash = password_hash
        self._rol = rol
        self._genero = genero
        self._telefono = telefono
        self._ubicacion = ubicacion
        self._foto_perfil = foto_perfil

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

    @property
    def genero(self) -> Optional[str]:
        return self._genero

    @property
    def telefono(self) -> Optional[str]:
        return self._telefono

    @property
    def ubicacion(self) -> Optional[str]:
        return self._ubicacion

    @property
    def foto_perfil(self) -> Optional[str]:
        return self._foto_perfil

    @foto_perfil.setter
    def foto_perfil(self, val: Optional[str]) -> None:
        self._foto_perfil = val

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
        descripcion_movilidad: str = "",
        perfil_medico: str = "Condición estable",
        descripcion_habitos: str = "",
        alergias: str = "Ninguna",
        imc: float = 22.0,
        dificultades_cognitivas: str = "Ninguna",
        fecha_nacimiento: Optional[str] = None,
        genero: Optional[str] = None,
        telefono: Optional[str] = None,
        ubicacion: Optional[str] = None,
        foto_perfil: Optional[str] = None,
        user_id: Optional[int] = None,
    ) -> None:
        super().__init__(nombre, correo, password_hash, "Adulto Mayor", genero, telefono, ubicacion, foto_perfil, user_id)
        self._descripcion_movilidad = descripcion_movilidad
        self._perfil_medico = perfil_medico
        self._descripcion_habitos = descripcion_habitos
        self._alergias = alergias
        self._imc = imc
        self._dificultades_cognitivas = dificultades_cognitivas
        self._fecha_nacimiento = fecha_nacimiento

    @property
    def fecha_nacimiento(self) -> Optional[str]:
        return self._fecha_nacimiento

    @property
    def descripcion_movilidad(self) -> str:
        return self._descripcion_movilidad

    @descripcion_movilidad.setter
    def descripcion_movilidad(self, val: str) -> None:
        self._descripcion_movilidad = val

    @property
    def perfil_medico(self) -> str:
        return self._perfil_medico

    @property
    def descripcion_habitos(self) -> str:
        return self._descripcion_habitos

    @property
    def dieta(self) -> str:
        return self._dieta

    @property
    def sueno(self) -> str:
        return self._sueno

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
        genero: Optional[str] = None,
        telefono: Optional[str] = None,
        ubicacion: Optional[str] = None,
        foto_perfil: Optional[str] = None,
        user_id: Optional[int] = None,
    ) -> None:
        super().__init__(nombre, correo, password_hash, "Familiar", genero, telefono, ubicacion, foto_perfil, user_id)
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
        tipo_cuidador: str = "",
        genero: Optional[str] = None,
        telefono: Optional[str] = None,
        ubicacion: Optional[str] = None,
        foto_perfil: Optional[str] = None,
        user_id: Optional[int] = None,
    ) -> None:
        super().__init__(nombre, correo, password_hash, "Cuidador", genero, telefono, ubicacion, foto_perfil, user_id)
        self._cedula_medica = cedula_medica
        self._tipo_cuidador = tipo_cuidador

    @property
    def cedula_medica(self) -> str:
        return self._cedula_medica

    @property
    def tipo_cuidador(self) -> str:
        return self._tipo_cuidador

    def panel_destino(self) -> str:
        return "cuidador"


class Administrador(Usuario):
    """Superusuario para mantenimiento del sistema."""

    def __init__(
        self,
        nombre: str,
        correo: str,
        password_hash: str,
        genero: Optional[str] = None,
        telefono: Optional[str] = None,
        ubicacion: Optional[str] = None,
        foto_perfil: Optional[str] = None,
        user_id: Optional[int] = None,
    ) -> None:
        super().__init__(nombre, correo, password_hash, "Administrador", genero, telefono, ubicacion, foto_perfil, user_id)

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
        genero = datos.get("genero")
        telefono = datos.get("telefono")
        ubicacion = datos.get("ubicacion")
        foto_perfil = datos.get("foto_perfil")

        if rol == "Adulto Mayor":
            return AdultoMayor(
                nombre, correo, pwd,
                descripcion_movilidad=datos.get("descripcion_movilidad", ""),
                perfil_medico=datos.get("perfil_medico", "Condición estable"),
                descripcion_habitos=datos.get("descripcion_habitos", ""),
                alergias=datos.get("alergias", "Ninguna"),
                imc=float(datos.get("imc", 22.0)),
                dificultades_cognitivas=datos.get("dificultades_cognitivas", "Ninguna"),
                fecha_nacimiento=datos.get("fecha_nacimiento"),
                genero=genero,
                telefono=telefono,
                ubicacion=ubicacion,
                foto_perfil=foto_perfil,
                user_id=uid,
            )
        if rol == "Familiar":
            return Familiar(
                nombre, correo, pwd,
                id_adulto_vinculado=datos.get("id_adulto_vinculado"),
                genero=genero,
                telefono=telefono,
                ubicacion=ubicacion,
                foto_perfil=foto_perfil,
                user_id=uid,
            )
        if rol in ("Cuidador", "Médico"):
            return Cuidador(
                nombre, correo, pwd,
                cedula_medica=datos.get("cedula_medica", "MED-0000"),
                tipo_cuidador=datos.get("tipo_cuidador", ""),
                genero=genero,
                telefono=telefono,
                ubicacion=ubicacion,
                foto_perfil=foto_perfil,
                user_id=uid,
            )
        if rol == "Administrador":
            return Administrador(
                nombre, correo, pwd,
                genero=genero,
                telefono=telefono,
                ubicacion=ubicacion,
                foto_perfil=foto_perfil,
                user_id=uid
            )
        return AdultoMayor(nombre, correo, pwd, user_id=uid)
