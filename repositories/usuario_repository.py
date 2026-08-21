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
               u.genero, u.telefono, u.ubicacion, u.foto_perfil,
               am.fecha_nacimiento,
               COALESCE(am.descripcion_movilidad, '') AS descripcion_movilidad,
               COALESCE(am.perfil_medico, '') AS perfil_medico,
               COALESCE(am.descripcion_habitos, '') AS descripcion_habitos,
               COALESCE(am.imc, 22.0) AS imc,
               COALESCE(c.cedula_medica, '') AS cedula_medica,
               COALESCE(tc.nombre, '') AS tipo_cuidador,
               COALESCE(c.id_tipo_cuidador, 1) AS id_tipo_cuidador,
               COALESCE(c.especialidad, '') AS especialidad,
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
               COALESCE((
                   SELECT GROUP_CONCAT(ant.nombre ORDER BY ant.nombre SEPARATOR ', ')
                   FROM adulto_antecedente aa
                   JOIN antecedente_medico ant ON ant.id = aa.id_antecedente
                   WHERE aa.id_adulto = am.id
               ), 'Ninguno') AS antecedentes_medicos,
               COALESCE((
                   SELECT ce.nombre FROM contacto_emergencia ce WHERE ce.id_adulto = am.id LIMIT 1
               ), '') AS contacto_emergencia_nombre,
               COALESCE((
                   SELECT ce.telefono FROM contacto_emergencia ce WHERE ce.id_adulto = am.id LIMIT 1
               ), '') AS contacto_emergencia_telefono,
               (SELECT rf.id_adulto FROM relaciones_familiar rf
                JOIN familiar f ON rf.id_familiar = f.id
                WHERE f.id_usuario = u.id AND rf.autorizado = 1
                ORDER BY rf.fecha_vinculo DESC LIMIT 1) AS id_adulto_vinculado
        FROM usuarios u
        LEFT JOIN adulto_mayor am ON am.id_usuario = u.id
        LEFT JOIN cuidador c ON c.id_usuario = u.id
        LEFT JOIN tipo_cuidador tc ON c.id_tipo_cuidador = tc.id_tipo_cuidador
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
                """INSERT INTO usuarios (nombre, correo, password_hash, rol, genero, telefono, ubicacion, foto_perfil)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                (usuario.nombre, usuario.correo, usuario.password_hash, usuario.rol, getattr(usuario, "genero", None), getattr(usuario, "telefono", None), getattr(usuario, "ubicacion", None), getattr(usuario, "foto_perfil", None)),
            )
            usuario.id = cursor.lastrowid
            if usuario.rol == "Adulto Mayor":
                cursor.execute(
                    """INSERT INTO adulto_mayor
                       (id_usuario, fecha_nacimiento, descripcion_movilidad, perfil_medico, descripcion_habitos, imc)
                       VALUES (%s, %s, %s, %s, %s, %s)""",
                    (
                        usuario.id,
                        datos_extra.get("fecha_nacimiento") or None,
                        datos_extra.get("descripcion_movilidad") or "",
                        datos_extra.get("perfil_medico") or "",
                        datos_extra.get("descripcion_habitos") or "",
                        datos_extra.get("imc") or 22.0,
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
                self._guardar_relaciones_salud(
                    cursor, adulto_id, "antecedente_medico", datos_extra.get("antecedentes_medicos"),
                    "adulto_antecedente", "id_antecedente",
                )
                # Contacto de emergencia opcional
                contacto_nombre = datos_extra.get("contacto_emergencia_nombre") or datos_extra.get("contacto_emergencia")
                contacto_telefono = datos_extra.get("contacto_emergencia_telefono") or ""
                if contacto_nombre:
                    cursor.execute(
                        "INSERT INTO contacto_emergencia (id_adulto, nombre, telefono, relacion) VALUES (%s, %s, %s, %s)",
                        (adulto_id, contacto_nombre, contacto_telefono, datos_extra.get("contacto_relacion", "Familiar")),
                    )
            elif usuario.rol in ("Cuidador", "Médico"):
                id_tipo = datos_extra.get("id_tipo_cuidador") or 1
                cursor.execute(
                    "INSERT INTO cuidador (id_usuario, cedula_medica, especialidad, id_tipo_cuidador) VALUES (%s, %s, %s, %s)",
                    (usuario.id, datos_extra.get("cedula_medica") or None, datos_extra.get("especialidad") or None, id_tipo),
                )
            elif usuario.rol == "Familiar":
                cursor.execute("INSERT INTO familiar (id_usuario) VALUES (%s)", (usuario.id,))
                familiar_id = cursor.lastrowid
                id_adulto_user = datos_extra.get("id_adulto_vinculado")
                if id_adulto_user:
                    cursor.execute("SELECT id FROM adulto_mayor WHERE id_usuario = %s", (id_adulto_user,))
                    row = cursor.fetchone()
                    if row:
                        adulto_id = row[0]
                        tipo_relacion = datos_extra.get("tipo_relacion", "Familiar")
                        cursor.execute(
                            "INSERT INTO relaciones_familiar (id_familiar, id_adulto, tipo_relacion, autorizado) VALUES (%s, %s, %s, 1)",
                            (familiar_id, adulto_id, tipo_relacion)
                        )
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

    def buscar_por_identificador(self, correo_o_nombre: str) -> Optional[dict]:
        rows = self._db.ejecutar_mysql(
            self._SELECT_USUARIO + " WHERE u.correo = %s OR u.nombre = %s",
            (correo_o_nombre, correo_o_nombre),
        )
        return rows[0] if rows else None

    def autenticar(self, correo_o_nombre: str, password_raw: str) -> Optional[dict]:
        row = self.buscar_por_identificador(correo_o_nombre)
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
        permitidos_usuario = {"nombre", "correo", "rol", "password_hash", "genero", "telefono", "ubicacion", "foto_perfil"}
        permitidos_adulto = {
            "fecha_nacimiento", "descripcion_movilidad", "perfil_medico", "descripcion_habitos", "imc"
        }
        permitidos_cuidador = {"cedula_medica", "especialidad", "id_tipo_cuidador"}
        
        user_fields = {k: v for k, v in campos.items() if k in permitidos_usuario}
        adult_fields = {k: v for k, v in campos.items() if k in permitidos_adulto}
        cuidador_fields = {k: v for k, v in campos.items() if k in permitidos_cuidador}
        
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
            if cuidador_fields:
                sets = ", ".join(f"{field} = %s" for field in cuidador_fields)
                cursor.execute(
                    f"UPDATE cuidador SET {sets} WHERE id_usuario = %s",
                    (*cuidador_fields.values(), user_id),
                )
            if "alergias" in campos or "dificultades_cognitivas" in campos or "antecedentes_medicos" in campos:
                cursor.execute("SELECT id FROM adulto_mayor WHERE id_usuario = %s", (user_id,))
                adulto = cursor.fetchone()
                if adulto:
                    adulto_id = adulto[0]
                    if "alergias" in campos:
                        cursor.execute("DELETE FROM adulto_alergia WHERE id_adulto = %s", (adulto_id,))
                        self._guardar_relaciones_salud(
                            cursor, adulto_id, "alergia", campos["alergias"], "adulto_alergia", "id_alergia"
                        )
                    if "dificultades_cognitivas" in campos:
                        cursor.execute("DELETE FROM adulto_dificultad WHERE id_adulto = %s", (adulto_id,))
                        self._guardar_relaciones_salud(
                            cursor, adulto_id, "dificultad_cognitiva", campos["dificultades_cognitivas"],
                            "adulto_dificultad", "id_dificultad"
                        )
                    if "antecedentes_medicos" in campos:
                        cursor.execute("DELETE FROM adulto_antecedente WHERE id_adulto = %s", (adulto_id,))
                        self._guardar_relaciones_salud(
                            cursor, adulto_id, "antecedente_medico", campos["antecedentes_medicos"],
                            "adulto_antecedente", "id_antecedente"
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

    def vincular_familiar(self, id_familiar_user: int, id_adulto_user: int, tipo_relacion: str = "Familiar") -> bool:
        conn = self._db.obtener_conexion_mysql()
        if not conn:
            return False
        try:
            cursor = conn.cursor()
            conn.start_transaction()
            cursor.execute("INSERT IGNORE INTO familiar (id_usuario) VALUES (%s)", (id_familiar_user,))
            cursor.execute("SELECT id FROM familiar WHERE id_usuario = %s", (id_familiar_user,))
            fam_row = cursor.fetchone()
            cursor.execute("SELECT id FROM adulto_mayor WHERE id_usuario = %s", (id_adulto_user,))
            ad_row = cursor.fetchone()
            if fam_row and ad_row:
                cursor.execute(
                    """INSERT INTO relaciones_familiar (id_familiar, id_adulto, tipo_relacion, autorizado)
                       VALUES (%s, %s, %s, 1) ON DUPLICATE KEY UPDATE autorizado = 1""",
                    (fam_row[0], ad_row[0], tipo_relacion),
                )
                conn.commit()
                cursor.close()
                conn.close()
                return True
            conn.rollback()
            conn.close()
            return False
        except Exception:
            conn.rollback()
            conn.close()
            return False

    def familiar_autorizado(self, id_familiar_user: int, id_adulto_user: int) -> bool:
        rows = self._db.ejecutar_mysql(
            """SELECT rf.id FROM relaciones_familiar rf
               JOIN familiar f ON rf.id_familiar = f.id
               JOIN adulto_mayor am ON rf.id_adulto = am.id
               WHERE f.id_usuario = %s AND am.id_usuario = %s AND rf.autorizado = 1""",
            (id_familiar_user, id_adulto_user),
        )
        return bool(rows)

    @staticmethod
    def dict_a_usuario(data: dict) -> Usuario:
        return UsuarioFactory.crear_usuario(data)
