"""Modelo de comunidad — mensajes y publicaciones."""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Mensaje:
    id_autor: int
    contenido: str
    fecha_hora: datetime
    estado: str = "visible"
    id: Optional[int] = None
    nombre_autor: str = ""


@dataclass
class Publicacion:
    id_autor: int
    contenido: str
    fecha_hora: datetime
    estado: str = "visible"
    id: Optional[int] = None
    nombre_autor: str = ""
