"""Repositorio de comunidad."""
from datetime import datetime
from typing import List, Tuple

from core.database import BaseDatosService
from core.messages import MensajeMITA


class ComunidadRepository:
    def __init__(self, db: BaseDatosService) -> None:
        self._db = db

    def obtener_publicaciones(self) -> Tuple[List[Tuple[str, str]], str]:
        posts = []
        rows = self._db.ejecutar_mysql(
            """SELECT p.contenido, u.nombre AS nombre_autor
               FROM publicaciones p
               JOIN usuarios u ON p.id_autor = u.id
               WHERE p.estado = 'visible'
               ORDER BY p.fecha_hora DESC LIMIT 50"""
        ) or []
        for row in rows:
            posts.append((row["nombre_autor"], row["contenido"]))

        if not posts:
            posts = [
                ("Dr. Pérez", "Recuerden realizar sus estiramientos matutinos."),
                ("Comunidad MITA", "Bienvenidos. Compartan sus logros del día."),
            ]
        return posts, MensajeMITA.BIENVENIDA_COMUNIDAD.value

    def enviar_publicacion(self, id_autor: int, nombre_autor: str, contenido: str) -> str:
        if not contenido.strip():
            return MensajeMITA.CAMPOS_OBLIGATORIOS.value
        ahora = datetime.now().isoformat()
        result = self._db.ejecutar_mysql(
            "INSERT INTO publicaciones (id_autor, contenido, fecha_hora, estado) VALUES (%s,%s,%s,'visible')",
            (id_autor, contenido, ahora),
        )
        return MensajeMITA.MENSAJE_ENVIADO.value if result is not None else MensajeMITA.ERROR_GUARDAR.value
