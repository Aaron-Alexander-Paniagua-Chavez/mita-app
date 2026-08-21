"""Persistencia de progreso — lectura desde vw_progreso y escritura en registro_actividad."""
from datetime import datetime

from core.database import BaseDatosService


class ProgresoRepository:
    def __init__(self, db: BaseDatosService) -> None:
        self._db = db

    def obtener_progreso_vista(self, id_usuario: int) -> dict:
        """Devuelve estadísticas calculadas en tiempo real desde vw_progreso.

        vw_progreso agrega los datos de registro_actividad; es la única fuente
        de lectura de estadísticas de progreso. Si no hay registros para el
        usuario se devuelven valores cero por defecto.
        """
        rows = self._db.ejecutar_mysql("SELECT * FROM vw_progreso WHERE id_usuario = %s", (id_usuario,))
        if rows:
            return rows[0]
        return {
            "id_usuario": id_usuario,
            "puntos": 0,
            "actividades_completadas": 0,
            "cognitivas_completadas": 0,
            "fisicas_completadas": 0,
            "ultima_actividad": None,
        }

    def registrar_historial(
        self, id_usuario: int, tipo: str, titulo: str, puntos: int,
        hora_inicio: str = None, hora_fin: str = None,
        nivel_alcanzado: int = None, desempeno: str = None,
        id_actividad: int = None
    ) -> bool:
        """Registra una actividad completada en registro_actividad (fuente de datos reales)."""
        return self._db.ejecutar_mysql(
            """INSERT INTO registro_actividad
               (id_usuario, id_actividad, fecha, hora_inicio, hora_fin, nivel_alcanzado, desempeno, puntos, observaciones)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (id_usuario, id_actividad, datetime.now(),
             hora_inicio, hora_fin, nivel_alcanzado or 1, desempeno or "Bueno", puntos, titulo),
        ) is not None

    def metricas_pacientes(self, ids: list) -> list:
        """Agrega métricas de progreso para una lista de pacientes, leyendo de vw_progreso."""
        resultado = []
        for uid in ids:
            progreso = self.obtener_progreso_vista(uid)
            usuario = self._db.ejecutar_mysql("SELECT nombre FROM usuarios WHERE id = %s", (uid,))
            nombre = usuario[0]["nombre"] if usuario else f"Paciente #{uid}"
            resultado.append({
                "id": uid,
                "nombre": nombre,
                "actividades": progreso.get("actividades_completadas", 0),
                "racha": 0,  # La racha se calcula en memoria por GestorProgreso (lógica de días consecutivos)
                "puntos": progreso.get("puntos", 0),
            })
        return resultado
