"""Servicio para filtrar actividades según preferencias y limitaciones del usuario.

Utiliza la tabla existente preferencias_usuario para almacenar limitaciones
y preferencias de actividades sin modificar el esquema de actividades.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, List

from repositories.preferencias_repository import PreferenciasRepository

if TYPE_CHECKING:
    from models.actividad import Actividad


class ActivityFilterService:
    """Filtra y adapta actividades según las preferencias y limitaciones del usuario."""

    def __init__(self, preference_repo: PreferenciasRepository) -> None:
        self._preference_repo = preference_repo

    def filtrar_actividades(
        self,
        actividades: List[Actividad],
        usuario_id: int
    ) -> List[Actividad]:
        """Filtra una lista de actividades según las limitaciones del usuario.

        Args:
            actividades: Lista de actividades a filtrar
            usuario_id: ID del usuario para obtener sus preferencias

        Returns:
            Lista de actividades que el usuario puede realizar según sus limitaciones
        """
        preferencias = self._preference_repo.obtener(usuario_id)

        # Obtener limitaciones de movimiento
        descripcion_movilidad = preferencias.get("descripcion_movilidad", "").lower()

        # Obtener dificultades cognitivas
        dificultades_cognitivas = preferencias.get("dificultades_cognitivas", "").lower()

        # Obtener actividades excluidas explícitamente
        actividades_excluidas = preferencias.get("actividades_excluidas", [])

        actividades_filtradas = []

        for actividad in actividades:
            if self._puede_realizar_actividad(
                actividad,
                descripcion_movilidad,
                dificultades_cognitivas,
                actividades_excluidas
            ):
                actividades_filtradas.append(actividad)

        return actividades_filtradas

    def _puede_realizar_actividad(
        self,
        actividad: Actividad,
        descripcion_movilidad: str,
        dificultades_cognitivas: str,
        actividades_excluidas: List[str]
    ) -> bool:
        """Determina si un usuario puede realizar una actividad específica."""

        # Exclusión explícita por nombre o etiquetas
        if actividad.titulo.lower() in [excl.lower() for excl in actividades_excluidas]:
            return False

        if any(excl.lower() in [etq.lower() for etq in actividad.etiquetas]
               for excl in actividades_excluidas):
            return False

        # Filtrar por limitaciones de movimiento
        if descripcion_movilidad and descripcion_movilidad != "ninguna":
            actividad_tipo = getattr(actividad, 'tipo', '').lower()
            actividad_categoria = getattr(actividad, 'categoria', '').lower()
            actividad_etiquetas = [etq.lower() for etq in getattr(actividad, 'etiquetas', [])]

            # Check if activity involves restricted movements
            texto_actividad = f"{actividad_tipo} {actividad_categoria} {' '.join(actividad_etiquetas)}".lower()

            zonas_afectadas: Set[str] = set()

            # Mapeo de términos comunes a zonas
            if 'rodilla' in descripcion_movilidad:
                zonas_afectadas.update(["rodillas", "piernas", "equilibrio", "sentarse"])
                
            if 'espalda' in descripcion_movilidad:
                zonas_afectadas.update(["espalda", "giros", "inclinacion"])
                
            if 'cadera' in descripcion_movilidad:
                zonas_afectadas.update(["cadera", "equilibrio", "caminar", "piernas"])

            if any(zona in texto_actividad for zona in zonas_afectadas):
                return False

        # Filtrar por dificultades cognitivas
        if dificultades_cognitivas and dificultades_cognitivas != "ninguna":
            # Las actividades ya vienen categorizadas por nivel y tipo
            # Podemos ajustar la complejidad basada en las dificultades
            actividad_nivel = getattr(actividad, 'nivel', 1)
            actividad_tipo = getattr(actividad, 'tipo', '').lower()

            # Para dificultades cognitivas, preferir actividades de nivel bajo
            if ('memoria' in dificultades_cognitivas or
                'alzheimer' in dificultades_cognitivas or
                'demencia' in dificultades_cognitivas) and actividad_nivel > 2:
                # Reducir nivel efectivo para actividades cognitivas altas
                if actividad_tipo == 'cognitiva':
                    return False  # Filtrar actividades cognitivas complejas

        return True

    def obtener_sugerencias_personalizadas(
        self,
        actividades: List[Actividad],
        usuario_id: int,
        limite: int = 5
    ) -> List[Actividad]:
        """Obtiene sugerencias de actividades personalizadas para el usuario."""

        preferencias = self._preference_repo.obtener(usuario_id)
        intereses = preferencias.get("intereses", [])

        # Filtrar actividades disponibles
        actividades_disponibles = self.filtrar_actividades(actividades, usuario_id)

        if not intereses:
            # Si no hay intereses específicos, devolver las primeras actividades disponibles
            return actividades_disponibles[:limite]

        # Priorizar actividades que coincidan con intereses
        actividades_con_interes = []
        actividades_sin_interes = []

        for actividad in actividades_disponibles:
            actividad_texto = f"{actividad.titulo} {getattr(actividad, 'descripcion', '')} {' '.join(getattr(actividad, 'etiquetas', []))}".lower()

            if any(interes.lower() in actividad_texto for interes in intereses):
                actividades_con_interes.append(actividad)
            else:
                actividades_sin_interes.append(actividad)

        # Combinar: primero las que coinciden con intereses, luego las demás
        resultado = actividades_con_interes + actividades_sin_interes
        return resultado[:limite]

    def guardar_limitaciones_usuario(
        self,
        usuario_id: int,
        descripcion_movilidad: str = "",
        dificultades_cognitivas: str = "",
        actividades_excluidas: List[str] = None
    ) -> bool:
        """Guarda las limitaciones y preferencias del usuario en preferencias_usuario."""

        if actividades_excluidas is None:
            actividades_excluidas = []

        preferencias_actuales = self._preference_repo.obtener(usuario_id)
        
        actualizaciones = {
            "descripcion_movilidad": descripcion_movilidad.strip(),
            "dificultades_cognitivas": dificultades_cognitivas.strip(),
            "actividades_excluidas": [a.lower().strip() for a in (actividades_excluidas or []) if a.strip()]
        }
        
        # Eliminar campos vacíos si no están explícitamente configurados
        actualizaciones = {k: v for k, v in actualizaciones.items() if v}
        
        preferencias_actuales.update(actualizaciones)

        return self._preference_repo.guardar(usuario_id, preferencias_actuales)

    def obtener_limitaciones_usuario(self, usuario_id: int) -> dict:
        """Obtiene las limitaciones y preferencias actuales del usuario."""
        return self._preference_repo.obtener(usuario_id)