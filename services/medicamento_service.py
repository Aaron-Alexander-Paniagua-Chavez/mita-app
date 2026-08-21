"""Lógica de negocio de tratamientos y adherencia (Nivel 9)."""
from datetime import date
from typing import Optional
from repositories.medicamento_repository import MedicamentoRepository
from repositories.notificacion_repository import NotificacionRepository


class MedicamentoService:
    def __init__(self, repo: MedicamentoRepository, notif_repo: Optional[NotificacionRepository] = None):
        self._repo = repo
        self._notif_repo = notif_repo

    def registrar_tratamiento(
        self, id_adulto: int, id_medicamento: int, dosis: str, frecuencia: str, id_cuidador: int = None
    ) -> bool:
        return self._repo.crear_tratamiento(id_adulto, id_medicamento, dosis, frecuencia, id_cuidador=id_cuidador)

    def registrar_toma(
        self, id_tratamiento: int, estado: str, hora_programada: str = None, hora_real: str = None, observaciones: str = None
    ) -> bool:
        return self._repo.registrar_toma(
            id_tratamiento, estado, hora_programada=hora_programada, hora_real=hora_real, observaciones=observaciones
        )

    def obtener_adherencia(self, id_adulto: int, fecha_desde: date, fecha_hasta: date) -> dict:
        completadas, totales = self._repo.calcular_adherencia(id_adulto, fecha_desde, fecha_hasta)
        porcentaje = (completadas / totales * 100) if totales > 0 else 0
        return {
            "total_tomas": totales,
            "tomas_completadas": completadas,
            "porcentaje_adherencia": round(porcentaje, 2),
            "nivel": "Óptimo" if porcentaje >= 90 else "Regular" if porcentaje >= 70 else "Crítico",
        }

    def obtener_adherencia_detalle(self, id_adulto: int) -> list[dict]:
        """Obtiene resumen detallado desde la vista SQL vw_adherencia_medicacion."""
        return self._repo.obtener_adherencia_vista(id_adulto)
