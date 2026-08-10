"""Persistencia MySQL de progreso y actividades completadas."""
from datetime import datetime

from core.database import BaseDatosService


class ProgresoRepository:
    def __init__(self, db: BaseDatosService) -> None:
        self._db = db

    @staticmethod
    def _nuevo_progreso(id_usuario: int) -> dict:
        return {
            "id_usuario": id_usuario,
            "puntos": 0,
            "racha_dias": 0,
            "actividades_completadas": 0,
            "cognitivas_completadas": 0,
        }

    def obtener_progreso(self, id_usuario: int) -> dict:
        rows = self._db.ejecutar_mysql("SELECT * FROM progreso WHERE id_usuario = %s", (id_usuario,))
        if rows:
            return rows[0]
        self._db.ejecutar_mysql("INSERT IGNORE INTO progreso (id_usuario) VALUES (%s)", (id_usuario,))
        return self._nuevo_progreso(id_usuario)

    def guardar_progreso(self, id_usuario: int, datos: dict) -> bool:
        result = self._db.ejecutar_mysql(
            """UPDATE progreso SET puntos=%s, racha_dias=%s, actividades_completadas=%s,
               cognitivas_completadas=%s, ultima_actividad=%s WHERE id_usuario=%s""",
            (
                datos["puntos"], datos["racha_dias"], datos["actividades_completadas"],
                datos["cognitivas_completadas"], datos.get("ultima_actividad"), id_usuario,
            ),
        )
        return result is not None

    def registrar_historial(self, id_usuario: int, tipo: str, titulo: str, puntos: int) -> bool:
        return self._db.ejecutar_mysql(
            """INSERT INTO actividades_historial
               (id_usuario, tipo_actividad, titulo, puntos, fecha_hora)
               VALUES (%s, %s, %s, %s, %s)""",
            (id_usuario, tipo, titulo, puntos, datetime.now().isoformat()),
        ) is not None

    def metricas_pacientes(self, ids: list) -> list:
        resultado = []
        for uid in ids:
            progreso = self.obtener_progreso(uid)
            usuario = self._db.ejecutar_mysql("SELECT nombre FROM usuarios WHERE id = %s", (uid,))
            nombre = usuario[0]["nombre"] if usuario else f"Paciente #{uid}"
            resultado.append({
                "id": uid,
                "nombre": nombre,
                "actividades": progreso.get("actividades_completadas", 0),
                "racha": progreso.get("racha_dias", 0),
                "puntos": progreso.get("puntos", 0),
            })
        return resultado
