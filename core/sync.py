"""Estado de sincronización para instalaciones MySQL locales o compartidas.

La aplicación no usa una cola SQLite. Cuando varias computadoras comparten el
mismo servidor MySQL de la red local, los cambios quedan disponibles en el
acto. La sincronización entre sedes se hará mediante la API segura descrita en
la documentación, no conectando clientes de escritorio a un MySQL público.
"""
from core.database import BaseDatosService


class GestorSincronizacionLocal:
    """Conserva el punto de extensión sin introducir otra base local."""

    def __init__(self, db: BaseDatosService) -> None:
        self._db = db

    def sincronizar_pendientes(self) -> int:
        """Verifica la disponibilidad del servidor MySQL actual.

        Un despliegue LAN usa un único MySQL compartido y por eso no tiene
        operaciones pendientes que replicar desde una base SQLite.
        """
        return 0 if self._db.hay_conexion_mysql() else -1
