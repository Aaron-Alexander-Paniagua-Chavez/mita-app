from core.database import BaseDatosService


class GestorSincronizacionLocal:
    def __init__(self, db: BaseDatosService) -> None:
        self._db = db

    def sincronizar_pendientes(self) -> int:
        return 0 if self._db.hay_conexion_mysql() else -1
