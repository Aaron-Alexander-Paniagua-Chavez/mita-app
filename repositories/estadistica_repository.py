"""Repositorio MongoDB de eventos dinámicos y telemetría de MITA."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from core.database import DatabaseManager


class EstadisticaRepository:
    """No impone esquema: valida sólo la colección que recibe el documento."""

    def __init__(self, db: DatabaseManager) -> None:
        self._db = db

    @staticmethod
    def _fecha(documento: dict[str, Any]) -> dict[str, Any]:
        documento.setdefault("fecha", datetime.now(timezone.utc))
        return documento

    def guardar_estadistica(self, documento: dict[str, Any]) -> bool:
        return self._insertar("estadisticas", documento)

    def guardar_metrica(self, documento: dict[str, Any]) -> bool:
        return self._insertar("metricas", documento)

    def iniciar_sesion(self, usuario: int, **contexto: Any) -> Optional[Any]:
        documento = self._fecha({"usuario": usuario, "inicio": datetime.now(timezone.utc), **contexto})
        collection = self._db.obtener_coleccion_mongo("sesiones")
        if collection is None:
            return None
        try:
            return collection.insert_one(documento).inserted_id
        except Exception:
            return None

    def cerrar_sesion(self, session_id: Any, duracion_segundos: int = 0) -> bool:
        if session_id is None:
            return False
        collection = self._db.obtener_coleccion_mongo("sesiones")
        if collection is None:
            return False
        try:
            result = collection.update_one(
                {"_id": session_id},
                {"$set": {
                    "fin": datetime.now(timezone.utc),
                    "duracion_segundos": max(0, int(duracion_segundos)),
                }},
            )
            return result.modified_count == 1
        except Exception:
            return False

    def registrar_evento(self, evento: str, usuario: Optional[int] = None, **datos: Any) -> bool:
        documento = {"evento": evento, "usuario": usuario, **datos}
        return self._insertar("telemetria", documento)

    def _insertar(self, collection_name: str, documento: dict[str, Any]) -> bool:
        collection = self._db.obtener_coleccion_mongo(collection_name)
        if collection is None:
            return False
        try:
            collection.insert_one(self._fecha(dict(documento)))
            return True
        except Exception:
            return False
