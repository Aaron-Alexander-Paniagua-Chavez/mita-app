"""Actividades adaptativas y seguras para los distintos perfiles de MITA."""
from __future__ import annotations

from abc import ABC, abstractmethod
from copy import deepcopy
from dataclasses import dataclass
from typing import Iterable, List


@dataclass(frozen=True)
class InstruccionVisual:
    """Un paso legible, con pista para la guía ilustrada y opcionalmente video."""

    orden: int
    texto: str
    icono: str = "📋"
    movimiento: str = "general"
    video_url: str = ""


class Actividad(ABC):
    """Contrato común. Los metadatos permiten filtrar antes de mostrar."""

    def __init__(
        self, titulo: str, impacto: str, categoria: str, etiquetas: Iterable[str] = (),
        duracion_sugerida_min: int = 5,
    ) -> None:
        self._titulo = titulo
        self._impacto = impacto
        self._categoria = categoria
        self._etiquetas = frozenset(e.lower() for e in etiquetas)
        self._duracion_sugerida_min = duracion_sugerida_min
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
    def etiquetas(self) -> frozenset[str]:
        return self._etiquetas

    @property
    def duracion_sugerida_min(self) -> int:
        return self._duracion_sugerida_min

    @property
    def instrucciones(self) -> List[InstruccionVisual]:
        return self._instrucciones

    @abstractmethod
    def obtener_instrucciones(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def iniciar(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def finalizar(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def ejecutar(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def calcular_puntuacion(self) -> int:
        raise NotImplementedError

    def mostrar_instrucciones(self) -> str:
        return self.obtener_instrucciones()


class EjercicioFisico(Actividad):
    def __init__(
        self, titulo: str, impacto: str, repeticiones: int = 10,
        etiquetas: Iterable[str] = (), duracion_sugerida_min: int = 5,
        pasos: Iterable[tuple[str, str, str]] = (),
    ) -> None:
        super().__init__(titulo, impacto, "fisico", etiquetas, duracion_sugerida_min)
        self._repeticiones = repeticiones
        pasos_defecto = (
            ("🪑", "Siéntate o usa un apoyo estable y adopta una postura cómoda.", "sentado"),
            ("🤸", f"Realiza hasta {repeticiones} repeticiones, despacio y sin forzar.", "movimiento"),
            ("🌬️", "Respira con calma; puedes descansar cuando lo necesites.", "respiracion"),
            ("🛑", "Si aparece dolor, mareo o inseguridad, detente y pide apoyo.", "seguridad"),
        )
        self._instrucciones = [
            InstruccionVisual(i + 1, texto, icono, movimiento)
            for i, (icono, texto, movimiento) in enumerate(tuple(pasos) or pasos_defecto)
        ]

    def obtener_instrucciones(self) -> str:
        return "\n\n".join(f"{i.orden}. {i.icono} {i.texto}" for i in self._instrucciones)

    def iniciar(self) -> str:
        return f"Iniciando {self._titulo}"

    def finalizar(self) -> str:
        return "Rutina física finalizada"

    def ejecutar(self) -> str:
        return "Ejecutando rutina física adaptada."

    def calcular_puntuacion(self) -> int:
        return 12 if self._impacto == "Bajo" else 15


class EjercicioCognitivo(Actividad):
    def __init__(
        self, titulo: str, nivel_dificultad: int = 1, etiquetas: Iterable[str] = (),
        duracion_sugerida_min: int = 5,
    ) -> None:
        super().__init__(titulo, "Bajo", "cognitivo", etiquetas, duracion_sugerida_min)
        self._nivel_dificultad = nivel_dificultad
        self._historial_desempeno: List[bool] = []
        self._instrucciones = [
            InstruccionVisual(1, "Observa la consigna y elige un lugar tranquilo.", "👀", "observar"),
            InstruccionVisual(2, "Responde sin prisa. Puedes pedir una pista o tomar una pausa.", "🧠", "pensar"),
            InstruccionVisual(3, f"Nivel actual: {nivel_dificultad}. Lo importante es intentarlo.", "📊", "progreso"),
        ]

    @property
    def nivel_dificultad(self) -> int:
        return self._nivel_dificultad

    def adaptar_dificultad(self, acierto: bool) -> None:
        self._historial_desempeno.append(acierto)
        aciertos = sum(self._historial_desempeno[-5:])
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
        return "Iniciando estímulo cognitivo adaptado."

    def calcular_puntuacion(self) -> int:
        return 10 + self._nivel_dificultad * 2


class AdaptadorEjercicios:
    """Excluye preventivamente actividades incompatibles con el perfil.

    Las exclusiones son apoyo de seguridad, no una prescripción. La persona o
    su profesional puede actualizar limitaciones desde Configuración.
    """

    CATALOGO_FISICO = [
        EjercicioFisico("Respiración consciente", "Bajo", 5, {"respiracion", "sentado"}, 3),
        EjercicioFisico("Manos activas", "Bajo", 12, {"manos", "sentado"}, 4),
        EjercicioFisico("Movilidad de hombros", "Bajo", 8, {"brazos", "hombros", "sentado"}, 5),
        EjercicioFisico("Estiramiento de brazos", "Bajo", 10, {"brazos", "sentado"}, 5),
        EjercicioFisico("Estiramiento de cuello", "Bajo", 6, {"cuello", "sentado"}, 3),
        EjercicioFisico("Postura sentada", "Bajo", 5, {"sentado", "espalda"}, 4),
        EjercicioFisico("Baile sentado", "Bajo", 10, {"sentado", "brazos", "ritmo"}, 6),
        EjercicioFisico("Movilidad de tobillos", "Bajo", 10, {"tobillos", "piernas", "sentado"}, 4),
        EjercicioFisico("Elevación de talones", "Bajo", 10, {"tobillos", "piernas", "equilibrio"}, 4),
        EjercicioFisico("Estiramiento de pantorrilla", "Bajo", 8, {"piernas", "rodillas", "equilibrio"}, 5),
        EjercicioFisico("Tai chi básico", "Bajo", 8, {"equilibrio", "piernas", "brazos"}, 7),
        EjercicioFisico("Caminata ligera guiada", "Bajo", 1, {"caminar", "piernas", "rodillas"}, 5),
        EjercicioFisico("Paso lateral con apoyo", "Medio", 8, {"piernas", "rodillas", "equilibrio"}, 5),
        EjercicioFisico("Equilibrio con respaldo", "Medio", 6, {"piernas", "rodillas", "equilibrio"}, 4),
        EjercicioFisico("Sentarse y levantarse", "Medio", 8, {"piernas", "rodillas", "sentarse"}, 5),
        EjercicioFisico("Caminata por intervalos", "Medio", 1, {"caminar", "piernas", "rodillas"}, 10),
    ]

    CATALOGO_COGNITIVO = [
        EjercicioCognitivo("Orientación del día", 1, {"orientacion", "atencion"}, 3),
        EjercicioCognitivo("Reconocer emociones", 1, {"emociones", "lenguaje"}, 4),
        EjercicioCognitivo("Buscar diferencias", 1, {"atencion", "vision"}, 4),
        EjercicioCognitivo("Palabras por categoría", 1, {"lenguaje", "asociacion"}, 5),
        EjercicioCognitivo("Lectura acompañada", 1, {"lenguaje", "comprension"}, 5),
        EjercicioCognitivo("Juego de memoria", 1, {"memoria", "atencion"}, 5),
        EjercicioCognitivo("Identificación de figuras", 1, {"vision", "atencion"}, 4),
        EjercicioCognitivo("Sopa de letras suave", 2, {"lenguaje", "atencion"}, 6),
        EjercicioCognitivo("Rompecabezas de figuras", 2, {"planificacion", "vision"}, 6),
        EjercicioCognitivo("Patrones de colores", 2, {"atencion", "memoria"}, 5),
        EjercicioCognitivo("Cálculo cotidiano", 2, {"calculo", "atencion"}, 5),
        EjercicioCognitivo("Planificar una receta", 2, {"planificacion", "secuencias"}, 6),
        EjercicioCognitivo("Nombres y lugares", 2, {"memoria", "lenguaje"}, 5),
        EjercicioCognitivo("Ordenar una historia", 2, {"secuencias", "memoria"}, 6),
        EjercicioCognitivo("Secuencias numéricas", 3, {"memoria", "calculo", "secuencias"}, 6),
    ]

    @staticmethod
    def _palabras(texto: str) -> set[str]:
        normalizado = (texto or "").lower().translate(str.maketrans("áéíóúüñ", "aeiouun"))
        return set(normalizado.replace(",", " ").replace("/", " ").split())

    @classmethod
    def filtrar_fisicos(cls, limitaciones: str, nivel_movilidad: str):
        from core.messages import MensajeMITA

        palabras = cls._palabras(limitaciones)
        movilidad_baja = cls._palabras(nivel_movilidad) & {"reducida", "baja", "limitada"}
        zonas_excluidas: set[str] = set()
        if palabras & {"rodilla", "rodillas", "pierna", "piernas", "cadera", "caminar", "movilidad"}:
            zonas_excluidas |= {"rodillas", "piernas", "caminar", "equilibrio", "sentarse", "tobillos"}
        if palabras & {"hombro", "hombros", "brazo", "brazos", "muneca", "mano", "manos"}:
            zonas_excluidas |= {"brazos", "hombros", "manos"}
        if movilidad_baja:
            zonas_excluidas |= {"piernas", "rodillas", "caminar", "equilibrio", "sentarse"}
        actividades = [
            deepcopy(actividad) for actividad in cls.CATALOGO_FISICO
            if not actividad.etiquetas.intersection(zonas_excluidas)
        ]
        if zonas_excluidas:
            return actividades, MensajeMITA.ACTIVIDADES_ADAPTADAS.value
        return actividades, "Catálogo completo disponible"

    @classmethod
    def filtrar_cognitivos(cls, dificultades: str):
        from core.messages import MensajeMITA

        palabras = cls._palabras(dificultades)
        excluir_memoria = bool(palabras & {"memoria", "alzheimer", "alzhaimer", "demencia"})
        excluir_atencion = bool(palabras & {"atencion", "concentracion"})
        excluidas = set()
        if excluir_memoria:
            excluidas.add("memoria")
        if excluir_atencion:
            excluidas.add("atencion")
        actividades = [
            deepcopy(actividad) for actividad in cls.CATALOGO_COGNITIVO
            if not actividad.etiquetas.intersection(excluidas)
        ]
        if excluidas:
            return actividades, MensajeMITA.ACTIVIDADES_ADAPTADAS.value
        return actividades, "Catálogo completo disponible"

    @classmethod
    def cognitivos(cls):
        return [deepcopy(actividad) for actividad in cls.CATALOGO_COGNITIVO]
