"""Modelo de actividades — polimorfismo y estrategia (RF04, RF11, RF12)."""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List


@dataclass
class InstruccionVisual:
    """Paso estructurado con texto e ícono/imagen."""
    orden: int
    texto: str
    icono: str = "📋"
    imagen_ref: str = ""


class Actividad(ABC):
    """Contrato común para todas las actividades."""

    def __init__(self, titulo: str, impacto: str, categoria: str) -> None:
        self._titulo = titulo
        self._impacto = impacto
        self._categoria = categoria
        self._instrucciones: List[InstruccionVisual] = []

    @property
    def titulo(self) -> str:
        return self._titulo

    @property
    def impacto(self) -> str:
        return self._impacto

    @property
    def categoria(self) -> str:
        return self._categoria

    @property
    def instrucciones(self) -> List[InstruccionVisual]:
        return self._instrucciones

    @abstractmethod
    def obtener_instrucciones(self) -> str:
        pass

    @abstractmethod
    def iniciar(self) -> str:
        pass

    @abstractmethod
    def finalizar(self) -> str:
        pass

    @abstractmethod
    def ejecutar(self) -> str:
        pass

    @abstractmethod
    def calcular_puntuacion(self) -> int:
        pass

    def mostrar_instrucciones(self) -> str:
        return self.obtener_instrucciones()


class EjercicioFisico(Actividad):
    def __init__(self, titulo: str, impacto: str, repeticiones: int = 10) -> None:
        super().__init__(titulo, impacto, "fisico")
        self._repeticiones = repeticiones
        self._instrucciones = [
            InstruccionVisual(1, "Siéntate en una silla cómoda con la espalda recta.", "🪑"),
            InstruccionVisual(2, f"Realiza {repeticiones} repeticiones a tu propio ritmo.", "🏃"),
            InstruccionVisual(3, "Respira profundamente entre cada movimiento.", "🌬️"),
            InstruccionVisual(4, "Si sientes dolor, detente inmediatamente.", "⚠️"),
        ]

    def obtener_instrucciones(self) -> str:
        return "\n\n".join(f"{i.orden}. {i.icono} {i.texto}" for i in self._instrucciones)

    def iniciar(self) -> str:
        return f"Iniciando {self._titulo}"

    def finalizar(self) -> str:
        return "Rutina física finalizada"

    def ejecutar(self) -> str:
        return "Ejecutando rutina de ejercicio físico adaptado."

    def calcular_puntuacion(self) -> int:
        return 15


class EjercicioCognitivo(Actividad):
    """Actividad cognitiva con dificultad adaptativa."""

    def __init__(self, titulo: str, nivel_dificultad: int = 1) -> None:
        super().__init__(titulo, "Bajo", "cognitivo")
        self._nivel_dificultad = nivel_dificultad
        self._historial_desempeno: List[bool] = []
        self._instrucciones = [
            InstruccionVisual(1, "Observa atentamente los patrones en pantalla.", "👀"),
            InstruccionVisual(2, "Selecciona la opción correcta sin prisa.", "🧠"),
            InstruccionVisual(3, f"Nivel actual: {nivel_dificultad}. Tómate tu tiempo.", "📊"),
        ]

    @property
    def nivel_dificultad(self) -> int:
        return self._nivel_dificultad

    def adaptar_dificultad(self, acierto: bool) -> None:
        self._historial_desempeno.append(acierto)
        aciertos = sum(1 for x in self._historial_desempeno[-5:] if x)
        if aciertos >= 4 and self._nivel_dificultad < 5:
            self._nivel_dificultad += 1
        elif aciertos <= 1 and self._nivel_dificultad > 1:
            self._nivel_dificultad -= 1

    def obtener_instrucciones(self) -> str:
        return "\n\n".join(f"{i.orden}. {i.icono} {i.texto}" for i in self._instrucciones)

    def iniciar(self) -> str:
        return f"Iniciando ejercicio cognitivo nivel {self._nivel_dificultad}"

    def finalizar(self) -> str:
        return "Ejercicio cognitivo finalizado"

    def ejecutar(self) -> str:
        return "Iniciando estímulo cognitivo y de memoria."

    def calcular_puntuacion(self) -> int:
        return 10 + self._nivel_dificultad * 2


class AdaptadorEjercicios:
    """Filtra catálogo según limitaciones del adulto mayor."""

    CATALOGO_FISICO = [
        EjercicioFisico("Estiramiento de Brazos (Bajo Impacto)", "Bajo", 10),
        EjercicioFisico("Caminata Ligera Guiada (5 mins)", "Bajo", 1),
        EjercicioFisico("Ejercicios de Respiración", "Bajo", 5),
        EjercicioFisico("Saltos de Tensión Muscular", "Alto", 15),
        EjercicioFisico("Sentadillas Moderadas", "Medio", 8),
    ]

    CATALOGO_COGNITIVO = [
        EjercicioCognitivo("Juego de Memoria (Cartas)", 1),
        EjercicioCognitivo("Sopa de Letras Básica", 2),
        EjercicioCognitivo("Identificación de Figuras", 1),
        EjercicioCognitivo("Secuencias Numéricas", 3),
    ]

    @classmethod
    def filtrar_fisicos(cls, limitaciones: str, nivel_movilidad: str):
        from core.messages import MensajeMITA

        actividades = list(cls.CATALOGO_FISICO)
        reducida = limitaciones.lower() not in ("ninguna", "", "normal")
        movilidad_baja = nivel_movilidad.lower() in ("reducida", "baja", "limitada")
        if reducida or movilidad_baja:
            actividades = [a for a in actividades if a.impacto != "Alto"]
            return actividades, MensajeMITA.ACTIVIDADES_ADAPTADAS.value
        return actividades, "Catálogo completo disponible"

    @classmethod
    def cognitivos(cls):
        return list(cls.CATALOGO_COGNITIVO)
