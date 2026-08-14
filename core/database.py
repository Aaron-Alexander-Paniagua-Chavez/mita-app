from __future__ import annotations

from contextlib import closing
from datetime import datetime, timezone
from typing import Any, Optional

try:
    import mysql.connector
    from mysql.connector import Error as MySQLError
except ImportError:
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

from config.settings import (
    MONGO_DATABASE,
    MONGO_URI,
    MYSQL_ADMIN_CONFIG,
    MYSQL_CONFIG,
    MYSQL_DATABASE,
    guardar_configuracion_mysql,
)
from core.security import GestorSeguridad
from database.mysql_schema import (
    CATALOGO_ACTIVIDADES,
    CATALOGO_ALERGIAS,
    CATALOGO_DIFICULTADES,
    CATALOGO_HABITOS,
    CATALOGO_MEDICAMENTOS,
    MYSQL_TABLE_DDL,
)


class DatabaseManager:
    def __init__(self) -> None:
        self.mysql_config = dict(MYSQL_CONFIG)
        self.mysql_admin_config = dict(MYSQL_ADMIN_CONFIG)
        self.mysql_ready = False
        self.mongo_ready = False
        self.mongo_client = None
        self.mongo_db = None
        self.startup_warnings: list[str] = []
        self.inicializar()

    def inicializar(self) -> None:
        self.mysql_ready = self._inicializar_mysql()
        self.mongo_ready = self._inicializar_mongo()

    def configurar_mysql(
        self,
        host: str,
        port: int,
        database: str,
        user: str,
        password: str,
        admin_user: str = "",
        admin_password: str = "",
    ) -> tuple[bool, str]:
        try:
            port = int(port)
            if not 1 <= port <= 65535:
                raise ValueError
        except (TypeError, ValueError):
            return False, "El puerto de MySQL debe estar entre 1 y 65535."

        host = host.strip() or "127.0.0.1"
        database = database.strip() or MYSQL_DATABASE
        user = user.strip() or "root"
        admin_user = admin_user.strip() or user
        admin_password = admin_password if admin_password else password
        if not self._nombre_base_valido(database):
            return False, "El nombre de la base sólo puede contener letras, números y guiones bajos."

        anterior_mysql = self.mysql_config
        anterior_admin = self.mysql_admin_config
        self.mysql_config = self._crear_configuracion(host, port, user, password, database)
        self.mysql_admin_config = self._crear_configuracion(host, port, admin_user, admin_password)
        self.mysql_ready = False
        self.startup_warnings.clear()
        if not self._inicializar_mysql():
            mensaje = self.startup_warnings[-1] if self.startup_warnings else "No fue posible conectar con MySQL."
            self.mysql_config = anterior_mysql
            self.mysql_admin_config = anterior_admin
            return False, mensaje

        guardar_configuracion_mysql(
            host, port, database, user, password, admin_user, admin_password
        )
        return True, "MySQL conectado. La base local está lista."

    @staticmethod
    def _crear_configuracion(
        host: str, port: int, user: str, password: str, database: Optional[str] = None
    ) -> dict[str, Any]:
        configuracion: dict[str, Any] = {
            "host": host,
            "port": port,
            "user": user,
            "password": password,
            "charset": "utf8mb4",
            "use_unicode": True,
            "connection_timeout": 3,
        }
        if database:
            configuracion["database"] = database
        return configuracion

    @staticmethod
    def _nombre_base_valido(nombre: str) -> bool:
        return bool(nombre) and nombre.replace("_", "").isalnum()

    def _agregar_aviso(self, aviso: str) -> None:
        if aviso not in self.startup_warnings:
            self.startup_warnings.append(aviso)

    def _inicializar_mysql(self) -> bool:
        if mysql is None:
            self._agregar_aviso("Falta instalar mysql-connector-python.")
            return False
        nombre = str(self.mysql_config.get("database") or MYSQL_DATABASE)
        if not self._nombre_base_valido(nombre):
            self._agregar_aviso("El nombre de la base MySQL no es válido.")
            return False
        try:
            with closing(mysql.connect(**self.mysql_admin_config)) as admin_conn:
                cursor = admin_conn.cursor()
                cursor.execute(
                    f"CREATE DATABASE IF NOT EXISTS `{nombre}` "
                    "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
                )
                admin_conn.commit()
                cursor.close()
            with closing(mysql.connect(**self.mysql_config)) as conn:
                self._crear_tablas_mysql(conn)
                self._crear_datos_iniciales(conn)
            return True
        except MySQLError as error:
            self._agregar_aviso(self._mensaje_mysql(error))
            return False

    @staticmethod
    def _mensaje_mysql(error: Exception) -> str:
        codigo = getattr(error, "errno", None)
        if codigo in {2002, 2003, 2005}:
            return "MySQL no está iniciado o no está disponible en 127.0.0.1:3306."
        if codigo in {1044, 1045}:
            return "MySQL rechazó la cuenta local. Abre Configurar MySQL e indica la contraseña de root."
        return "No fue posible crear o abrir la base local de MySQL."

    @staticmethod
    def _crear_tablas_mysql(conn) -> None:
        cursor = conn.cursor()
        try:
            for ddl in MYSQL_TABLE_DDL:
                cursor.execute(ddl)
            conn.commit()
        except MySQLError:
            conn.rollback()
            raise
        finally:
            cursor.close()

    @staticmethod
    def _crear_datos_iniciales(conn) -> None:
        usuarios = (
            ("Admin MITA", "admin@mita.local", "admin2026", "Administrador"),
            ("María López", "maria@mita.local", "mita2026", "Adulto Mayor"),
            ("Carlos López", "familiar@mita.local", "mita2026", "Familiar"),
            ("Dra. Elena Pérez", "cuidador@mita.local", "mita2026", "Cuidador"),
        )
        cursor = conn.cursor(dictionary=True)
        try:
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
            ids = {fila["correo"]: fila["id"] for fila in cursor.fetchall()}
            adulto_id = ids["maria@mita.local"]
            cuidador_id = ids["cuidador@mita.local"]
            familiar_id = ids["familiar@mita.local"]
            cursor.execute(
                """INSERT INTO adulto_mayor
                   (id_usuario, limitaciones_movilidad, perfil_medico, imc, nivel_movilidad)
                   VALUES (%s, %s, %s, %s, %s)
                   ON DUPLICATE KEY UPDATE id_usuario = id_usuario""",
                (adulto_id, "Rodilla delicada", "Perfil inicial.", 22.0, "Reducida"),
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
                   ON DUPLICATE KEY UPDATE activa = 1""",
                CATALOGO_ACTIVIDADES,
            )
            cursor.executemany(
                """INSERT INTO alergia (nombre, descripcion) VALUES (%s, %s)
                   ON DUPLICATE KEY UPDATE nombre = VALUES(nombre)""",
                CATALOGO_ALERGIAS,
            )
            cursor.executemany(
                """INSERT INTO habito (nombre, descripcion, categoria) VALUES (%s, %s, %s)
                   ON DUPLICATE KEY UPDATE nombre = VALUES(nombre)""",
                CATALOGO_HABITOS,
            )
            cursor.executemany(
                """INSERT INTO dificultad_cognitiva (nombre, descripcion) VALUES (%s, %s)
                   ON DUPLICATE KEY UPDATE nombre = VALUES(nombre)""",
                CATALOGO_DIFICULTADES,
            )
            cursor.executemany(
                """INSERT INTO medicamento (nombre, presentacion, indicaciones) VALUES (%s, %s, %s)
                   ON DUPLICATE KEY UPDATE nombre = VALUES(nombre)""",
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
        except MySQLError:
            conn.rollback()
            raise
        finally:
            cursor.close()

    def _inicializar_mongo(self) -> bool:
        if MongoClient is None:
            self._agregar_aviso("MongoDB no está disponible; la telemetría no se guardará.")
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
                {"evento": "inicio_mita"},
                {"$setOnInsert": {
                    "evento": "inicio_mita",
                    "fecha": datetime.now(timezone.utc),
                }},
                upsert=True,
            )
            self.mongo_client = client
            self.mongo_db = db
            return True
        except PyMongoError:
            self._agregar_aviso("MongoDB no está disponible; la telemetría no se guardará.")
            return False

    def obtener_coleccion_mongo(self, coleccion: str):
        if not self.mongo_ready or self.mongo_db is None:
            return None
        if coleccion not in {"estadisticas", "metricas", "sesiones", "telemetria"}:
            raise ValueError("Colección MongoDB no permitida.")
        return self.mongo_db[coleccion]

    def hay_conexion_mysql(self) -> bool:
        if not self.mysql_ready:
            self.mysql_ready = self._inicializar_mysql()
        conexion = self.obtener_conexion_mysql()
        if conexion is None:
            return False
        conexion.close()
        return True

    def obtener_conexion_mysql(self):
        if mysql is None:
            return None
        if not self.mysql_ready:
            self.mysql_ready = self._inicializar_mysql()
            if not self.mysql_ready:
                return None
        try:
            return mysql.connect(**self.mysql_config)
        except MySQLError:
            self.mysql_ready = False
            self._agregar_aviso("Se perdió la conexión con MySQL.")
            return None

    def ejecutar_mysql(self, sql: str, params: tuple = ()) -> Optional[Any]:
        conexion = self.obtener_conexion_mysql()
        if conexion is None:
            return None
        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute(sql, params)
            instruccion = sql.lstrip().split(maxsplit=1)[0].upper() if sql.strip() else ""
            if instruccion in {"SELECT", "SHOW", "DESCRIBE", "EXPLAIN"}:
                resultado: Any = cursor.fetchall()
            else:
                conexion.commit()
                resultado = cursor.lastrowid
            cursor.close()
            conexion.close()
            return resultado
        except MySQLError:
            conexion.rollback()
            conexion.close()
            return None


BaseDatosService = DatabaseManager
