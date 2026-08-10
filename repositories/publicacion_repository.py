"""Nombre explícito del repositorio de publicaciones de comunidad."""
from repositories.comunidad_repository import ComunidadRepository


class PublicacionRepository(ComunidadRepository):
    """Mantiene compatibilidad con ComunidadRepository durante la transición."""
