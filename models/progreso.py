"""Progreso, logros y reportes — gamificación y visualización (RF05, RF08–RF10)."""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import List, Optional, Tuple

from core.messages import MensajeMITA
from models.actividad import Actividad
from models.usuario import Usuario, AdultoMayor


@dataclass
class Logro:
    id: str
    titulo: str
    descripcion: str
    criterio: str
    desbloqueado: bool = False
    icono: str = "🏅"


class GestorProgreso:
    """Registra actividades, puntos y rachas."""

    def __init__(self) -> None:
        self.puntos: int = 0
        self.racha_dias: int = 0
        self.actividades_completadas: int = 0
        self.cognitivas_completadas: int = 0
        self._ultima_fecha: Optional[date] = None
        self._historial: List[dict] = []

    def cargar_desde_db(self, datos: dict) -> None:
        if not datos:
            return
        self.puntos = datos.get("puntos", 0)
        self.racha_dias = datos.get("racha_dias", 0)
        self.actividades_completadas = datos.get("actividades_completadas", 0)
        self.cognitivas_completadas = datos.get("cognitivas_completadas", 0)
        ultima = datos.get("ultima_actividad")
        if ultima:
            try:
                self._ultima_fecha = datetime.fromisoformat(str(ultima)).date()
            except ValueError:
                self._ultima_fecha = None

    def registrar_actividad(self, actividad: Actividad) -> Tuple[int, str]:
        pts = actividad.calcular_puntuacion()
        self.puntos += pts
        self.actividades_completadas += 1
        if actividad.categoria == "cognitivo":
            self.cognitivas_completadas += 1
        self._actualizar_racha()
        self._historial.append({
            "titulo": actividad.titulo,
            "puntos": pts,
            "fecha": datetime.now().isoformat(),
            "tipo": actividad.categoria,
        })
        return self.puntos, MensajeMITA.EXCELENTE_TRABAJO.value

    def _actualizar_racha(self) -> None:
        hoy = date.today()
        if self._ultima_fecha is None:
            self.racha_dias = 1
        elif self._ultima_fecha == hoy:
            pass
        elif (hoy - self._ultima_fecha).days == 1:
            self.racha_dias += 1
        else:
            self.racha_dias = 1
        self._ultima_fecha = hoy

    def to_dict(self) -> dict:
        return {
            "puntos": self.puntos,
            "racha_dias": self.racha_dias,
            "actividades_completadas": self.actividades_completadas,
            "cognitivas_completadas": self.cognitivas_completadas,
            "ultima_actividad": self._ultima_fecha.isoformat() if self._ultima_fecha else None,
        }


class SistemaLogros:
    """Evalúa criterios y desbloquea insignias."""

    def __init__(self) -> None:
        self.logros: List[Logro] = [
            Logro("primer_dia", "Primer Día", "Completaste tu primer ejercicio.", "actividades>=1", icono="🏅"),
            Logro("mente_activa", "Mente Activa", "Terminaste 5 ejercicios cognitivos.", "cognitivas>=5", icono="🏆"),
            Logro("constancia", "Constancia", "Racha de 3 días conectándote.", "racha>=3", icono="⭐"),
            Logro("activo", "Usuario Activo", "Acumulaste 80 puntos.", "puntos>=80", icono="🌟"),
        ]

    def evaluar(self, progreso: GestorProgreso) -> Tuple[bool, str]:
        nuevo = False
        for logro in self.logros:
            if logro.desbloqueado:
                continue
            if self._cumple(logro.criterio, progreso):
                logro.desbloqueado = True
                nuevo = True
        if nuevo:
            return True, MensajeMITA.LOGRO_DESBLOQUEADO.value
        return False, ""

    @staticmethod
    def _cumple(criterio: str, p: GestorProgreso) -> bool:
        if criterio == "actividades>=1":
            return p.actividades_completadas >= 1
        if criterio == "cognitivas>=5":
            return p.cognitivas_completadas >= 5
        if criterio == "racha>=3":
            return p.racha_dias >= 3
        if criterio == "puntos>=80":
            return p.puntos >= 80
        return False


class Reporte(ABC):
    @abstractmethod
    def generar_resumen(self, usuario: Usuario, progreso: GestorProgreso) -> str:
        pass


class ReporteFamiliar(Reporte):
    def generar_resumen(self, usuario: Usuario, progreso: GestorProgreso) -> str:
        return (
            f"Resumen de {usuario.nombre}:\n"
            f"• Actividades completadas: {progreso.actividades_completadas}\n"
            f"• Racha: {progreso.racha_dias} días\n"
            f"• Puntos: {progreso.puntos}\n"
            f"(Sin datos médicos sensibles)"
        )


class ReporteCuidador(Reporte):
    def generar_resumen(self, usuario: Usuario, progreso: GestorProgreso) -> str:
        extra = ""
        if isinstance(usuario, AdultoMayor):
            extra = (
                f"\n• Movilidad: {usuario.descripcion_movilidad}"
                f"\n• IMC: {usuario.imc}"
            )
        return (
            f"Expediente clínico-resumen — {usuario.nombre}\n"
            f"• Actividades: {progreso.actividades_completadas}\n"
            f"• Cognitivas: {progreso.cognitivas_completadas}\n"
            f"• Racha: {progreso.racha_dias} días\n"
            f"• Puntos: {progreso.puntos}{extra}"
        )


class PanelCuidador:
    """Agrega métricas para el panel profesional."""

    @staticmethod
    def recopilar_metricas(pacientes: List[dict]) -> Tuple[dict, str]:
        total_act = sum(p.get("actividades", 0) for p in pacientes)
        promedio_racha = (
            sum(p.get("racha", 0) for p in pacientes) / len(pacientes) if pacientes else 0
        )
        return {
            "total_pacientes": len(pacientes),
            "total_actividades": total_act,
            "promedio_racha": round(promedio_racha, 1),
        }, MensajeMITA.ESTADISTICAS_CUIDADOR.value
