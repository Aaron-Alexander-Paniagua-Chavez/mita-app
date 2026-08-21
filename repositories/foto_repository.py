"""Gestión segura de fotos de perfil en sistema de archivos local (LOCALAPPDATA/MITA/fotos/)."""
import os
import shutil
import uuid
from pathlib import Path
from typing import Optional, Tuple

from config.settings import APP_DATA_ROOT


class FotoRepository:
    MAX_TAMANO_BYTES = 5 * 1024 * 1024  # 5 MB

    def __init__(self) -> None:
        self.fotos_dir = APP_DATA_ROOT / "fotos"
        self.fotos_dir.mkdir(parents=True, exist_ok=True)
        self.extensiones_permitidas = {".jpg", ".jpeg", ".png", ".webp"}

    def validar_imagen(self, ruta_origen: Path) -> Tuple[bool, str]:
        if not ruta_origen.exists() or not ruta_origen.is_file():
            return False, "El archivo seleccionado no existe."

        # Prevención de Path Traversal
        filename = ruta_origen.name
        if ".." in filename or "/" in filename or "\\" in filename:
            return False, "Nombre de archivo inválido."

        # Validación de extensión
        ext = ruta_origen.suffix.lower()
        if ext not in self.extensiones_permitidas:
            return False, f"Formato no permitido. Format os aceptados: {', '.join(self.extensiones_permitidas)}"

        # Validación de tamaño máximo (5MB)
        if ruta_origen.stat().st_size > self.MAX_TAMANO_BYTES:
            return False, "La imagen supera el tamaño máximo permitido de 5 MB."

        return True, "Válido"

    def guardar_foto(self, origen_path: str, user_id: int) -> Tuple[bool, str]:
        """Guarda una foto para un usuario con sanitización y seguridad."""
        ruta_origen = Path(origen_path)
        valido, msj = self.validar_imagen(ruta_origen)
        if not valido:
            return False, msj

        ext = ruta_origen.suffix.lower()
        nombre_seguro = f"user_{user_id}_{uuid.uuid4().hex[:8]}{ext}"
        destino = self.fotos_dir / nombre_seguro

        try:
            shutil.copy2(ruta_origen, destino)
            return True, str(destino.resolve())
        except Exception as e:
            return False, f"Error al guardar la imagen: {str(e)}"

    def eliminar_foto(self, ruta_foto: str) -> bool:
        if not ruta_foto:
            return True
        try:
            p = Path(ruta_foto).resolve()
            # Prevención de path traversal
            if self.fotos_dir.resolve() not in p.parents and p != self.fotos_dir.resolve():
                return False
            if p.exists() and p.is_file():
                p.unlink()
            return True
        except Exception:
            return False

    def obtener_avatar_predeterminado() -> str:
        return "👤"
