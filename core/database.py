"""Inicialización y acceso a los servicios de datos de MITA.

MySQL es obligatorio y es la única base de datos relacional que usa la
aplicación, incluso cuando se instala en una sola computadora sin Internet.
MongoDB es opcional y sólo recibe telemetría no clínica. No existe respaldo ni
persistencia de ejecución en SQLite.
"""
from __future__ import annotations

from contextlib import closing
from datetime import datetime, timezone
from typing import Any, Optional

try:
    import mysql.connector
    from mysql.connector import Error as MySQLError
except ImportError:  # La UI puede informar la configuración pendiente.
    mysql = None
    MySQLError = Exception
else:
    mysql = mysql.connector

try:
    from pymongo import ASCENDING, MongoClient
    from pymongo.errors import PyMongoError
except ImportError:
    ASCENDING = 1
    MongoClient = None
    PyMongoError = Exception

from config.settings import MONGO_DATABASE, MONGO_URI, MYSQL_CONFIG, MYSQL_DATABASE
from core.security import GestorSeguridad
from database.mysql_schema import (
    CATALOGO_ACTIVIDADES,
    CATALOGO_ALERGIAS,
    CATALOGO_DIFICULTADES,
    CATALOGO_HABITOS,
    CATALOGO_MEDICAMENTOS,
    MYSQL_TABLE_DDL,
    SCHEMA_VERSION,
)


class DatabaseManager:
    """Coordina conexiones y migraciones sin degradar los datos a otro motor."""

    _LEGACY_DATABASES = ("mita", "mita_pruebas")

    def __init__(self) -> None:
        self.mysql_config = dict(MYSQL_CONFIG)
        self.mysql_ready = False
        self.mongo_ready = False
        self.mongo_client = None
        self.mongo_db = None
        self.startup_warnings: list[str] = []
        self.inicializar()

    def inicializar(self) -> None:
        """Prepara MySQL y, si está disponible, la telemetría en MongoDB."""
        self.mysql_ready = self._inicializar_mysql()
        self.mongo_ready = self._inicializar_mongo()

    def _agregar_aviso(self, aviso: str) -> None:
        if aviso not in self.startup_warnings:
            self.startup_warnings.append(aviso)

    # ------------------------------------------------------------------
    # MySQL: base, estructura versionada, datos de demostración y migración
    # ------------------------------------------------------------------
    def _inicializar_mysql(self) -> bool:
        if mysql is None:
            self._agregar_aviso(
                "Falta instalar mysql-connector-python. MITA necesita MySQL para funcionar."
            )
            return False
        try:
            # En producción el usuario de aplicación sólo necesita permisos
            # sobre una base existente; evita exigir CREATE DATABASE cada vez.
            try:
                with closing(mysql.connect(**self.mysql_config)) as conn:
                    self._aplicar_migraciones(conn)
                    self._migrar_bases_legacy(conn)
                    self._insertar_datos_iniciales(conn)
                return True
            except MySQLError:
                pass

            # Primer arranque de desarrollo: una cuenta con privilegio CREATE
            # puede preparar la base antes de usar un usuario de aplicación.
            admin_config = dict(self.mysql_config)
            admin_config.pop("database", None)
            with closing(mysql.connect(**admin_config)) as admin_conn:
                admin_cursor = admin_conn.cursor()
                admin_cursor.execute(
                    f"CREATE DATABASE IF NOT EXISTS `{MYSQL_DATABASE}` "
                    "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
                )
                admin_conn.commit()
                admin_cursor.close()

            with closing(mysql.connect(**self.mysql_config)) as conn:
                self._aplicar_migraciones(conn)
                self._migrar_bases_legacy(conn)
                self._insertar_datos_iniciales(conn)
            return True
        except MySQLError:
            self._agregar_aviso(
                "No fue posible conectar con MySQL. Inicia el servicio y revisa MYSQL_* en .env; "
                "MITA no guarda datos en SQLite."
            )
            return False

    def _aplicar_migraciones(self, conn) -> None:
        cursor = conn.cursor()
        cursor.execute(MYSQL_TABLE_DDL[0])
        cursor.execute("SELECT version FROM schema_versions WHERE version = %s", (SCHEMA_VERSION,))
        if cursor.fetchone():
            cursor.close()
            return
        for ddl in MYSQL_TABLE_DDL[1:]:
            cursor.execute(ddl)
        cursor.execute("INSERT INTO schema_versions (version) VALUES (%s)", (SCHEMA_VERSION,))
        conn.commit()
        cursor.close()

    def _insertar_datos_iniciales(self, conn) -> None:
        """Carga roles, catálogos y ejemplos de forma idempotente."""
        usuarios = (
            ("Admin MITA", "admin@mita.local", "admin2026", "Administrador"),
            ("María López", "maria@mita.local", "mita2026", "Adulto Mayor"),
            ("Carlos López", "familiar@mita.local", "mita2026", "Familiar"),
            ("Dra. Elena Pérez", "cuidador@mita.local", "mita2026", "Cuidador"),
        )
        cursor = conn.cursor(dictionary=True)
        for nombre, correo, password, rol in usuarios:
            cursor.execute(
                """INSERT INTO usuarios (nombre, correo, password_hash, rol)
                   VALUES (%s, %s, %s, %s)
                   ON DUPLICATE KEY UPDATE id = LAST_INSERT_ID(id)""",
                (nombre, correo, GestorSeguridad.hashear_password(password), rol),
            )
        cursor.execute(
            "SELECT id, correo FROM usuarios WHERE correo IN (%s, %s, %s, %s)",
            tuple(item[1] for item in usuarios),
        )
        ids = {row["correo"]: row["id"] for row in cursor.fetchall()}

        adulto_id = ids["maria@mita.local"]
        cuidador_id = ids["cuidador@mita.local"]
        familiar_id = ids["familiar@mita.local"]
        cursor.execute(
            """INSERT INTO adulto_mayor
               (id_usuario, limitaciones_movilidad, perfil_medico, imc, nivel_movilidad)
               VALUES (%s, %s, %s, %s, %s)
               ON DUPLICATE KEY UPDATE id_usuario = id_usuario""",
            (adulto_id, "Rodilla delicada", "Perfil inicial de demostración.", 22.0, "Reducida"),
        )
        cursor.execute(
            """INSERT INTO cuidador (id_usuario, cedula_medica, especialidad)
               VALUES (%s, %s, %s)
               ON DUPLICATE KEY UPDATE id_usuario = id_usuario""",
            (cuidador_id, "MED-0001", "Geriatría"),
        )
        cursor.execute(
            """INSERT INTO relaciones_familiar (id_familiar, id_adulto, autorizado)
               VALUES (%s, %s, 1)
               ON DUPLICATE KEY UPDATE autorizado = 1""",
            (familiar_id, adulto_id),
        )
        for user_id in ids.values():
            cursor.execute("INSERT IGNORE INTO progreso (id_usuario) VALUES (%s)", (user_id,))

        cursor.executemany(
            """INSERT INTO actividad (nombre, descripcion, tipo, nivel, impacto)
               VALUES (%s, %s, %s, %s, %s)
               ON DUPLICATE KEY UPDATE descripcion = VALUES(descripcion), activa = 1""",
            CATALOGO_ACTIVIDADES,
        )
        cursor.executemany(
            """INSERT INTO alergia (nombre, descripcion) VALUES (%s, %s)
               ON DUPLICATE KEY UPDATE descripcion = VALUES(descripcion)""",
            CATALOGO_ALERGIAS,
        )
        cursor.executemany(
            """INSERT INTO habito (nombre, descripcion, categoria) VALUES (%s, %s, %s)
               ON DUPLICATE KEY UPDATE descripcion = VALUES(descripcion), categoria = VALUES(categoria)""",
            CATALOGO_HABITOS,
        )
        cursor.executemany(
            """INSERT INTO dificultad_cognitiva (nombre, descripcion) VALUES (%s, %s)
               ON DUPLICATE KEY UPDATE descripcion = VALUES(descripcion)""",
            CATALOGO_DIFICULTADES,
        )
        cursor.executemany(
            """INSERT INTO medicamento (nombre, presentacion, indicaciones) VALUES (%s, %s, %s)
               ON DUPLICATE KEY UPDATE indicaciones = VALUES(indicaciones)""",
            CATALOGO_MEDICAMENTOS,
        )
        cursor.execute(
            """INSERT INTO publicaciones (id_autor, contenido)
               SELECT %s, %s FROM DUAL
               WHERE NOT EXISTS (SELECT 1 FROM publicaciones WHERE contenido = %s)""",
            (cuidador_id, "Recuerden realizar sus estiramientos matutinos.",
             "Recuerden realizar sus estiramientos matutinos."),
        )
        cursor.execute(
            """INSERT INTO logros_usuario (id_usuario, id_logro)
               SELECT %s, %s FROM DUAL
               WHERE NOT EXISTS (
                   SELECT 1 FROM logros_usuario WHERE id_usuario = %s AND id_logro = %s
               )""",
            (adulto_id, "primer_dia", adulto_id, "primer_dia"),
        )
        conn.commit()
        cursor.close()

    def _migrar_bases_legacy(self, conn) -> None:
        """Copia usuarios de bases MySQL anteriores una sola vez, si existen."""
        cursor = conn.cursor(dictionary=True)
        for legacy in self._LEGACY_DATABASES:
            cursor.execute("SELECT 1 FROM migraciones_legacy WHERE base_origen = %s", (legacy,))
            if cursor.fetchone():
                continue
            cursor.execute(
                """SELECT 1 FROM information_schema.tables
                   WHERE table_schema = %s AND table_name = 'usuarios'""",
                (legacy,),
            )
            if not cursor.fetchone():
                continue
            cursor.execute(
                """SELECT column_name FROM information_schema.columns
                   WHERE table_schema = %s AND table_name = 'usuarios'""",
                (legacy,),
            )
            columns = {row["column_name"] for row in cursor.fetchall()}
            if not {"nombre", "correo"}.issubset(columns):
                incidencia = "No se encontraron las columnas nombre y correo requeridas."
                cursor.execute(
                    "INSERT INTO migraciones_legacy (base_origen, incidencias) VALUES (%s, %s)",
                    (legacy, incidencia),
                )
                self._agregar_aviso(f"No se migraron usuarios de {legacy}: {incidencia}")
                continue

            password_column = next(
                (column for column in ("password_hash", "contraseña", "password") if column in columns), None
            )
            role_column = "rol" if "rol" in columns else None
            selected = ["nombre", "correo"] + ([password_column] if password_column else [])
            if role_column:
                selected.append(role_column)
            fields = ", ".join(f"`{field}`" for field in selected)
            cursor.execute(f"SELECT {fields} FROM `{legacy}`.`usuarios`")
            migrated = 0
            issues: list[str] = []
            for row in cursor.fetchall():
                try:
                    password_hash = row.get(password_column) if password_column else ""
                    if not password_hash:
                        issues.append(f"{row.get('correo', 'sin correo')}: contraseña ausente")
                        continue
                    role = row.get(role_column) if role_column else "Adulto Mayor"
                    if role not in {"Administrador", "Adulto Mayor", "Cuidador", "Familiar"}:
                        role = "Adulto Mayor"
                    cursor.execute(
                        """INSERT INTO usuarios (nombre, correo, password_hash, rol)
                           VALUES (%s, %s, %s, %s)
                           ON DUPLICATE KEY UPDATE id = id""",
                        (row["nombre"], row["correo"], password_hash, role),
                    )
                    migrated += cursor.rowcount == 1
                except (KeyError, MySQLError):
                    issues.append(f"{row.get('correo', 'sin correo')}: fila inválida")
            detail = "; ".join(issues[:10]) or None
            cursor.execute(
                """INSERT INTO migraciones_legacy (base_origen, usuarios_migrados, incidencias)
                   VALUES (%s, %s, %s)""",
                (legacy, migrated, detail),
            )
            if issues:
                self._agregar_aviso(
                    f"{legacy}: se migraron {migrated} usuarios; {len(issues)} filas requieren revisión."
                )
        conn.commit()
        cursor.close()

    # ------------------------------------------------------------------
    # MongoDB: únicamente información dinámica no clínica.
    # ------------------------------------------------------------------
    def _inicializar_mongo(self) -> bool:
        if MongoClient is None:
            self._agregar_aviso("MongoDB no está disponible: no se registrará telemetría.")
            return False
        try:
            client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=1500)
            client.admin.command("ping")
            db = client[MONGO_DATABASE]
            db.estadisticas.create_index([("usuario", ASCENDING), ("fecha", ASCENDING)])
            db.metricas.create_index([("fecha", ASCENDING)])
            db.sesiones.create_index([("usuario", ASCENDING), ("inicio", ASCENDING)])
            db.telemetria.create_index([("evento", ASCENDING), ("fecha", ASCENDING)])
            db.telemetria.update_one(
                {"evento": "sistema_inicializado", "origen": "bootstrap"},
                {"$setOnInsert": {
                    "evento": "sistema_inicializado",
                    "origen": "bootstrap",
                    "fecha": datetime.now(timezone.utc),
                    "version_app": "MITA 2.1",
                }},
                upsert=True,
            )
            self.mongo_client = client
            self.mongo_db = db
            return True
        except PyMongoError:
            self._agregar_aviso("MongoDB no está disponible: no se registrará telemetría.")
            return False

    def obtener_coleccion_mongo(self, collection: str):
        if not self.mongo_ready or self.mongo_db is None:
            return None
        if collection not in {"estadisticas", "metricas", "sesiones", "telemetria"}:
            raise ValueError("Colección Mongo no permitida")
        return self.mongo_db[collection]

    # ------------------------------------------------------------------
    # API MySQL para repositorios
    # ------------------------------------------------------------------
    def hay_conexion_mysql(self) -> bool:
        conn = self.obtener_conexion_mysql()
        if not conn:
            return False
        conn.close()
        return True

    def obtener_conexion_mysql(self):
        if not self.mysql_ready or mysql is None:
            return None
        try:
            conn = mysql.connect(**self.mysql_config)
            if conn.is_connected():
                return conn
        except MySQLError:
            self.mysql_ready = False
            self._agregar_aviso(
                "Se perdió la conexión con MySQL. Los datos no se guardarán hasta reconectarse."
            )
        return None

    def ejecutar_mysql(self, sql: str, params: tuple = ()) -> Optional[Any]:
        conn = self.obtener_conexion_mysql()
        if not conn:
            return None
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(sql, params)
            if sql.lstrip().upper().startswith("SELECT"):
                result: Any = cursor.fetchall()
            else:
                conn.commit()
                result = cursor.lastrowid
            cursor.close()
            conn.close()
            return result
        except MySQLError:
            conn.close()
            return None


# Alias para no romper imports ya utilizados por la interfaz existente.
BaseDatosService = DatabaseManager
