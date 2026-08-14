"""Persistencia MySQL de usuarios y perfiles relacionales de MITA."""
from __future__ import annotations

from typing import List, Optional

from core.database import DatabaseManager
from core.security import GestorSeguridad
from models.usuario import Usuario, UsuarioFactory


class UsuarioRepository:
    """Único punto de acceso MySQL para usuarios, perfiles y permisos familiares."""

    _SELECT_USUARIO = """
        SELECT u.id, u.nombre, u.correo, u.password_hash, u.rol, u.fecha_registro,
               COALESCE(am.limitaciones_movilidad, 'Ninguna') AS limitaciones_movilidad,
               COALESCE(am.perfil_medico, '') AS perfil_medico,
               COALESCE(am.imc, 22.0) AS imc,
               COALESCE(am.nivel_movilidad, 'Normal') AS nivel_movilidad,
               COALESCE(c.cedula_medica, '') AS cedula_medica,
               COALESCE((
                   SELECT GROUP_CONCAT(a.nombre ORDER BY a.nombre SEPARATOR ', ')
                   FROM adulto_alergia aa
                   JOIN alergia a ON a.id = aa.id_alergia
                   WHERE aa.id_adulto = am.id
               ), 'Ninguna') AS alergias,
               COALESCE((
                   SELECT GROUP_CONCAT(dc.nombre ORDER BY dc.nombre SEPARATOR ', ')
                   FROM adulto_dificultad ad
                   JOIN dificultad_cognitiva dc ON dc.id = ad.id_dificultad
                   WHERE ad.id_adulto = am.id
               ), 'Ninguna') AS dificultades_cognitivas,
               (SELECT rf.id_adulto FROM relaciones_familiar rf
                   WHERE rf.id_familiar = u.id AND rf.autorizado = 1
                   ORDER BY rf.fecha_vinculo DESC LIMIT 1) AS id_adulto_vinculado
        FROM usuarios u
        LEFT JOIN adulto_mayor am ON am.id_usuario = u.id
        LEFT JOIN cuidador c ON c.id_usuario = u.id
    """

    def __init__(self, db: DatabaseManager) -> None:
        self._db = db

    def existe_correo(self, correo: str) -> bool:
        return bool(self._db.ejecutar_mysql("SELECT id FROM usuarios WHERE correo = %s", (correo,)))

    def guardar_usuario(self, usuario: Usuario, datos_extra: Optional[dict] = None) -> bool:
        return self._guardar_mysql(usuario, datos_extra or {})

    def _guardar_mysql(self, usuario: Usuario, datos_extra: dict) -> bool:
        conn = self._db.obtener_conexion_mysql()
        if not conn:
            return False
        try:
            cursor = conn.cursor()
            conn.start_transaction()
            cursor.execute(
                """INSERT INTO usuarios (nombre, correo, password_hash, rol)
                   VALUES (%s, %s, %s, %s)""",
                (usuario.nombre, usuario.correo, usuario.password_hash, usuario.rol),
            )
            usuario.id = cursor.lastrowid
            if usuario.rol == "Adulto Mayor":
                cursor.execute(
                    """INSERT INTO adulto_mayor
                       (id_usuario, limitaciones_movilidad, perfil_medico, imc, nivel_movilidad)
                       VALUES (%s, %s, %s, %s, %s)""",
                    (
                        usuario.id,
                        datos_extra.get("limitaciones_movilidad") or "Ninguna",
                        datos_extra.get("perfil_medico") or "",
                        datos_extra.get("imc") or 22.0,
                        datos_extra.get("nivel_movilidad") or "Normal",
                    ),
                )
                adulto_id = cursor.lastrowid
                self._guardar_relaciones_salud(
                    cursor, adulto_id, "alergia", datos_extra.get("alergias"), "adulto_alergia", "id_alergia"
                )
                self._guardar_relaciones_salud(
                    cursor, adulto_id, "dificultad_cognitiva", datos_extra.get("dificultades_cognitivas"),
                    "adulto_dificultad", "id_dificultad",
                )
            elif usuario.rol == "Cuidador":
                cursor.execute(
                    "INSERT INTO cuidador (id_usuario, cedula_medica) VALUES (%s, %s)",
                    (usuario.id, datos_extra.get("cedula_medica") or None),
                )
            cursor.execute("INSERT INTO progreso (id_usuario) VALUES (%s)", (usuario.id,))
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except Exception:
            conn.rollback()
            conn.close()
            return False

    @staticmethod
    def _guardar_relaciones_salud(cursor, adulto_id: int, catalogo: str, texto: Optional[str], relacion: str, columna: str) -> None:
        """Convierte las selecciones de la UI en relaciones normalizadas."""
        if not texto or texto.strip().lower() in {"ninguna", "ninguno", "normal"}:
            return
        for nombre in {part.strip() for part in texto.split(",") if part.strip()}:
            cursor.execute(
                f"INSERT INTO {catalogo} (nombre) VALUES (%s) ON DUPLICATE KEY UPDATE id = LAST_INSERT_ID(id)",
                (nombre,),
            )
            cursor.execute(
                f"INSERT IGNORE INTO {relacion} (id_adulto, {columna}) VALUES (%s, LAST_INSERT_ID())",
                (adulto_id,),
            )

    def autenticar(self, correo_o_nombre: str, password_raw: str) -> Optional[dict]:
        rows = self._db.ejecutar_mysql(
            self._SELECT_USUARIO + " WHERE u.correo = %s OR u.nombre = %s",
            (correo_o_nombre, correo_o_nombre),
        )
        row = rows[0] if rows else None
        if not row or not GestorSeguridad.verificar_password(password_raw, row["password_hash"]):
            return None
        if GestorSeguridad.requiere_actualizacion_hash(row["password_hash"]):
            nuevo_hash = GestorSeguridad.hashear_password(password_raw)
            self.actualizar_usuario(row["id"], {"password_hash": nuevo_hash})
            row["password_hash"] = nuevo_hash
        return row

    def listar_por_rol(self, rol: str) -> List[dict]:
        return self._db.ejecutar_mysql(
            self._SELECT_USUARIO + " WHERE u.rol = %s ORDER BY u.nombre", (rol,)
        ) or []

    def listar_todos(self) -> List[dict]:
        return self._db.ejecutar_mysql(
            "SELECT id, nombre, correo, rol FROM usuarios ORDER BY rol, nombre"
        ) or []

    def obtener_por_id(self, user_id: int) -> Optional[dict]:
        rows = self._db.ejecutar_mysql(self._SELECT_USUARIO + " WHERE u.id = %s", (user_id,))
        return rows[0] if rows else None

    def actualizar_usuario(self, user_id: int, campos: dict) -> bool:
        if not campos:
            return False
        permitidos_usuario = {"nombre", "correo", "rol", "password_hash"}
        permitidos_adulto = {"limitaciones_movilidad", "perfil_medico", "imc", "nivel_movilidad"}
        user_fields = {k: v for k, v in campos.items() if k in permitidos_usuario}
        adult_fields = {k: v for k, v in campos.items() if k in permitidos_adulto}
        if not user_fields and not adult_fields:
            return False
        conn = self._db.obtener_conexion_mysql()
        if not conn:
            return False
        try:
            cursor = conn.cursor()
            conn.start_transaction()
            if user_fields:
                sets = ", ".join(f"{field} = %s" for field in user_fields)
                cursor.execute(f"UPDATE usuarios SET {sets} WHERE id = %s", (*user_fields.values(), user_id))
            if adult_fields:
                sets = ", ".join(f"{field} = %s" for field in adult_fields)
                cursor.execute(
                    f"UPDATE adulto_mayor SET {sets} WHERE id_usuario = %s",
                    (*adult_fields.values(), user_id),
                )
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except Exception:
            conn.rollback()
            conn.close()
            return False

    def eliminar_usuario(self, user_id: int) -> bool:
        return self._db.ejecutar_mysql("DELETE FROM usuarios WHERE id = %s", (user_id,)) is not None

    def vincular_familiar(self, id_familiar: int, id_adulto: int) -> bool:
        result = self._db.ejecutar_mysql(
            """INSERT INTO relaciones_familiar (id_familiar, id_adulto, autorizado)
               VALUES (%s, %s, 1) ON DUPLICATE KEY UPDATE autorizado = 1""",
            (id_familiar, id_adulto),
        )
        return result is not None

    def familiar_autorizado(self, id_familiar: int, id_adulto: int) -> bool:
        rows = self._db.ejecutar_mysql(
            """SELECT id FROM relaciones_familiar
               WHERE id_familiar = %s AND id_adulto = %s AND autorizado = 1""",
            (id_familiar, id_adulto),
        )
        return bool(rows)

    @staticmethod
    def dict_a_usuario(data: dict) -> Usuario:
        return UsuarioFactory.crear_usuario(data)
