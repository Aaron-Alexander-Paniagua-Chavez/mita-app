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
    CATALOGO_ESTADO_TOMA,
    CATALOGO_HABITOS,
    CATALOGO_LOGROS,
    CATALOGO_MEDICAMENTOS,
    CATALOGO_ANTECEDENTES,
    CATALOGO_TIPO_ACTIVIDAD,
    CATALOGO_TIPO_CUIDADOR,
    CATALOGO_TIPO_METRICA,
    MYSQL_TABLE_DDL,
    MYSQL_VIEWS_DDL,
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
        return f"No fue posible crear o abrir la base local de MySQL: {error}"

    @staticmethod
    def _asegurar_columna(cursor, tabla: str, columna: str, definicion: str) -> None:
        cursor.execute(
            """SELECT COUNT(*) FROM information_schema.COLUMNS
               WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s AND COLUMN_NAME = %s""",
            (tabla, columna)
        )
        if not cursor.fetchone()[0]:
            cursor.execute(f"ALTER TABLE {tabla} ADD COLUMN {columna} {definicion}")

    @classmethod
    def _crear_tablas_mysql(cls, conn) -> None:
        cursor = conn.cursor()
        try:
            for ddl in MYSQL_TABLE_DDL:
                cursor.execute(ddl)

            # Migración de catálogos principales
            cursor.executemany(
                "INSERT INTO estado_toma (id_estado, nombre, descripcion) VALUES (%s, %s, %s) "
                "ON DUPLICATE KEY UPDATE nombre = VALUES(nombre), descripcion = VALUES(descripcion)",
                CATALOGO_ESTADO_TOMA,
            )
            cursor.executemany(
                "INSERT INTO tipo_actividad (id_tipo_actividad, nombre, descripcion) VALUES (%s, %s, %s) "
                "ON DUPLICATE KEY UPDATE nombre = VALUES(nombre), descripcion = VALUES(descripcion)",
                CATALOGO_TIPO_ACTIVIDAD,
            )
            cursor.executemany(
                "INSERT INTO tipo_cuidador (id_tipo_cuidador, nombre, descripcion) VALUES (%s, %s, %s) "
                "ON DUPLICATE KEY UPDATE nombre = VALUES(nombre), descripcion = VALUES(descripcion)",
                CATALOGO_TIPO_CUIDADOR,
            )
            cursor.executemany(
                "INSERT INTO logro (id, codigo, nombre, descripcion, puntos) VALUES (%s, %s, %s, %s, %s) "
                "ON DUPLICATE KEY UPDATE nombre = VALUES(nombre), descripcion = VALUES(descripcion), puntos = VALUES(puntos)",
                CATALOGO_LOGROS,
            )
            cursor.executemany(
                "INSERT INTO tipo_metrica (id_tipo_metrica, nombre, unidad_estandar, descripcion) VALUES (%s, %s, %s, %s) "
                "ON DUPLICATE KEY UPDATE nombre = VALUES(nombre), unidad_estandar = VALUES(unidad_estandar), descripcion = VALUES(descripcion)",
                CATALOGO_TIPO_METRICA,
            )

            # 1. Migrar registro_toma.estado -> id_estado
            cursor.execute(
                """SELECT COUNT(*) FROM information_schema.COLUMNS
                   WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'registro_toma' AND COLUMN_NAME = 'estado'"""
            )
            if cursor.fetchone()[0]:
                cursor.execute("UPDATE registro_toma SET id_estado = 1 WHERE estado = 'Programado'")
                cursor.execute("UPDATE registro_toma SET id_estado = 2 WHERE estado = 'Tomado'")
                cursor.execute("UPDATE registro_toma SET id_estado = 3 WHERE estado = 'Omitido'")
                cursor.execute("UPDATE registro_toma SET id_estado = 4 WHERE estado = 'Atrasado'")
                cursor.execute("ALTER TABLE registro_toma DROP COLUMN estado")

            # 2. Migrar actividad.tipo -> id_tipo_actividad
            cursor.execute(
                """SELECT COUNT(*) FROM information_schema.COLUMNS
                   WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'actividad' AND COLUMN_NAME = 'tipo'"""
            )
            if cursor.fetchone()[0]:
                cursor.execute("UPDATE actividad SET id_tipo_actividad = 1 WHERE tipo LIKE '%fisic%' OR tipo = '1'")
                cursor.execute("UPDATE actividad SET id_tipo_actividad = 2 WHERE tipo LIKE '%cognitiv%' OR tipo = '2'")
                try:
                    cursor.execute("ALTER TABLE actividad DROP INDEX uk_actividad_nombre_tipo")
                except MySQLError:
                    pass
                cursor.execute("ALTER TABLE actividad DROP COLUMN tipo")

            # 3. Migrar cuidador.tipo_cuidador (VARCHAR -> INT FK)
            cursor.execute(
                """SELECT DATA_TYPE FROM information_schema.COLUMNS
                   WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'cuidador' AND COLUMN_NAME = 'tipo_cuidador'"""
            )
            row = cursor.fetchone()
            if row and row[0].lower() in ("varchar", "char", "text"):
                cursor.execute("UPDATE cuidador SET id_tipo_cuidador = 1 WHERE tipo_cuidador LIKE '%médic%' OR tipo_cuidador LIKE '%medic%'")
                cursor.execute("UPDATE cuidador SET id_tipo_cuidador = 2 WHERE tipo_cuidador LIKE '%enfermer%'")
                cursor.execute("UPDATE cuidador SET id_tipo_cuidador = 3 WHERE tipo_cuidador LIKE '%terapeut%'")
                cursor.execute("UPDATE cuidador SET id_tipo_cuidador = 4 WHERE tipo_cuidador LIKE '%cuidador%'")
                cursor.execute("ALTER TABLE cuidador DROP COLUMN tipo_cuidador")

            # 4. Migrar logros_usuario.id_logro (VARCHAR -> INT FK)
            cursor.execute(
                """SELECT DATA_TYPE FROM information_schema.COLUMNS
                   WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'logros_usuario' AND COLUMN_NAME = 'id_logro'"""
            )
            row = cursor.fetchone()
            if row and row[0].lower() in ("varchar", "char", "text"):
                cursor.execute("ALTER TABLE logros_usuario ADD COLUMN id_logro_int INT NULL")
                cursor.fetchone()  # Consume result
                for l_id, l_code, _, _, _ in CATALOGO_LOGROS:
                    cursor.execute("UPDATE logros_usuario SET id_logro_int = %s WHERE id_logro = %s", (l_id, l_code))
                    cursor.fetchone()  # Consume result
                cursor.execute("DELETE FROM logros_usuario WHERE id_logro_int IS NULL")
                cursor.fetchone()  # Consume result
                cursor.execute("ALTER TABLE logros_usuario DROP COLUMN id_logro")
                cursor.fetchone()  # Consume result
                cursor.execute("ALTER TABLE logros_usuario CHANGE COLUMN id_logro_int id_logro INT NOT NULL")
                cursor.fetchone()  # Consume result
                try:
                    cursor.execute("ALTER TABLE logros_usuario ADD UNIQUE KEY uk_usuario_logro (id_usuario, id_logro)")
                    cursor.fetchone()  # Consume result
                except MySQLError:
                    pass

            # 5. Migrar actividades_historial -> registro_actividad
            cursor.execute(
                """SELECT COUNT(*) FROM information_schema.TABLES
                   WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'actividades_historial'"""
            )
            if cursor.fetchone()[0]:
                cursor.execute(
                    """INSERT INTO registro_actividad (id_usuario, id_actividad, fecha, hora_inicio, hora_fin, nivel_alcanzado, desempeno, puntos, observaciones)
                       SELECT id_usuario, id_actividad, fecha_hora, hora_inicio, hora_fin, nivel_alcanzado, desempeno, puntos, titulo
                       FROM actividades_historial"""
                )
                cursor.fetchone()  # Consume result
                cursor.execute("DROP TABLE actividades_historial")

            # 6. Migrar familiar & relaciones_familiar FKs
            cursor.execute(
                """INSERT IGNORE INTO familiar (id_usuario)
                   SELECT id FROM usuarios WHERE rol = 'Familiar'"""
            )
            cursor.fetchone()  # Consume result
            cursor.execute(
                """SELECT REFERENCED_TABLE_NAME
                   FROM information_schema.KEY_COLUMN_USAGE
                   WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'relaciones_familiar' AND COLUMN_NAME = 'id_familiar'"""
            )
            fk_row = cursor.fetchone()
            cursor.fetchone()  # Consume result
            if fk_row and fk_row[0] == "usuarios":
                cursor.execute(
                    """UPDATE relaciones_familiar rf
                       JOIN familiar f ON rf.id_familiar = f.id_usuario
                       JOIN adulto_mayor am ON rf.id_adulto = am.id_usuario
                       SET rf.id_familiar = f.id, rf.id_adulto = am.id"""
                )
                cursor.fetchone()  # Consume result
                try:
                    cursor.execute("ALTER TABLE relaciones_familiar DROP FOREIGN KEY fk_relacion_familiar")
                    cursor.fetchone()  # Consume result
                    cursor.execute("ALTER TABLE relaciones_familiar DROP FOREIGN KEY fk_relacion_adulto")
                    cursor.fetchone()  # Consume result
                except MySQLError:
                    pass
                cursor.execute(
                    """ALTER TABLE relaciones_familiar
                       ADD CONSTRAINT fk_relacion_familiar FOREIGN KEY (id_familiar) REFERENCES familiar(id) ON DELETE CASCADE,
                       ADD CONSTRAINT fk_relacion_adulto FOREIGN KEY (id_adulto) REFERENCES adulto_mayor(id) ON DELETE CASCADE"""
                )
                cursor.fetchone()  # Consume result

            # 7. Migrar adulto_mayor.dieta -> dieta_adulto
            cursor.execute(
                """SELECT COUNT(*) FROM information_schema.COLUMNS
                   WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'adulto_mayor' AND COLUMN_NAME = 'dieta'"""
            )
            if cursor.fetchone()[0]:
                cursor.execute(
                    """INSERT INTO dieta_adulto (id_adulto, descripcion, activa)
                       SELECT id, dieta, 1 FROM adulto_mayor WHERE dieta IS NOT NULL AND dieta != ''"""
                )
                cursor.execute("ALTER TABLE adulto_mayor DROP COLUMN dieta")

            # 8. Migrar adulto_mayor.sueno -> registro_sueno
            cursor.execute(
                """SELECT COUNT(*) FROM information_schema.COLUMNS
                   WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'adulto_mayor' AND COLUMN_NAME = 'sueno'"""
            )
            if cursor.fetchone()[0]:
                cursor.execute(
                    """INSERT INTO registro_sueno (id_adulto, fecha, observaciones)
                       SELECT id, CURRENT_DATE, sueno FROM adulto_mayor WHERE sueno IS NOT NULL AND sueno != ''"""
                )
                cursor.execute("ALTER TABLE adulto_mayor DROP COLUMN sueno")

            # 9. Migrar metrica_biometrica.tipo -> id_tipo_metrica (FK to tipo_metrica)
            cursor.execute(
                """SELECT COUNT(*) FROM information_schema.COLUMNS
                   WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'metrica_biometrica' AND COLUMN_NAME = 'tipo'"""
            )
            if cursor.fetchone()[0]:
                cursor.execute("SELECT COUNT(*) FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'metrica_biometrica' AND COLUMN_NAME = 'id_tipo_metrica'")
                if not cursor.fetchone()[0]:
                    cursor.execute("ALTER TABLE metrica_biometrica ADD COLUMN id_tipo_metrica INT NULL")

                cursor.execute("SELECT DISTINCT tipo FROM metrica_biometrica")
                tipos_existentes = [row[0] for row in cursor.fetchall()]
                for tipo_valor in tipos_existentes:
                    if tipo_valor is None:
                        continue
                    tipo_lower = tipo_valor.lower().strip()
                    id_tipo = None
                    if "frecuencia" in tipo_lower and ("cardiaca" in tipo_lower or "card" in tipo_lower or "heart" in tipo_lower):
                        id_tipo = 1
                    elif "peso" in tipo_lower or "weight" in tipo_lower:
                        id_tipo = 2
                    elif "saturaci" in tipo_lower or "ox" in tipo_lower or "spo2" in tipo_lower:
                        id_tipo = 3
                    elif "paso" in tipo_lower or "step" in tipo_lower:
                        id_tipo = 4
                    elif "sue" in tipo_lower or "sleep" in tipo_lower:
                        id_tipo = 5
                    else:
                        cursor.execute("INSERT IGNORE INTO tipo_metrica (nombre, descripcion) VALUES (%s, %s)",
                                       (tipo_valor, "Migrado de tipo desconocido"))
                        cursor.execute("SELECT id_tipo_metrica FROM tipo_metrica WHERE nombre = %s", (tipo_valor,))
                        row_tipo = cursor.fetchone()
                        if row_tipo:
                            id_tipo = row_tipo[0]

                    if id_tipo is not None:
                        cursor.execute("UPDATE metrica_biometrica SET id_tipo_metrica = %s WHERE tipo = %s", (id_tipo, tipo_valor))

                cursor.execute("DELETE FROM metrica_biometrica WHERE id_tipo_metrica IS NULL")
                cursor.execute("ALTER TABLE metrica_biometrica MODIFY id_tipo_metrica INT NOT NULL")
                try:
                    cursor.execute("ALTER TABLE metrica_biometrica ADD CONSTRAINT fk_metrica_tipo FOREIGN KEY (id_tipo_metrica) REFERENCES tipo_metrica(id_tipo_metrica) ON DELETE RESTRICT")
                except MySQLError:
                    pass
                cursor.execute("ALTER TABLE metrica_biometrica DROP COLUMN tipo")

            # 10. Eliminar tabla progreso (datos derivados, reemplazada por vw_progreso)
            cursor.execute(
                """SELECT COUNT(*) FROM information_schema.TABLES
                   WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'progreso'"""
            )
            if cursor.fetchone()[0]:
                cursor.execute("DROP TABLE progreso")

            # 11. Arreglar logros_usuario constraints and FKs (N:M relation)
            try:
                cursor.execute("ALTER TABLE logros_usuario DROP INDEX uk_usuario_logro")
            except MySQLError:
                pass
            try:
                cursor.execute("ALTER TABLE logros_usuario DROP INDEX id_usuario")
            except MySQLError:
                pass
            try:
                cursor.execute("ALTER TABLE logros_usuario ADD UNIQUE KEY uk_usuario_logro (id_usuario, id_logro)")
            except MySQLError:
                pass
            try:
                cursor.execute("ALTER TABLE logros_usuario ADD CONSTRAINT fk_logro_usuario FOREIGN KEY (id_usuario) REFERENCES usuarios(id) ON DELETE CASCADE")
            except MySQLError:
                pass
            try:
                cursor.execute("ALTER TABLE logros_usuario ADD CONSTRAINT fk_logros_usuario_logro FOREIGN KEY (id_logro) REFERENCES logro(id) ON DELETE RESTRICT")
            except MySQLError:
                pass

            # Crear Vistas SQL
            for vddl in MYSQL_VIEWS_DDL:
                cursor.execute(vddl)

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
            adulto_user_id = ids["maria@mita.local"]
            cuidador_user_id = ids["cuidador@mita.local"]
            familiar_user_id = ids["familiar@mita.local"]

            cursor.execute(
                """INSERT INTO adulto_mayor
                   (id_usuario, descripcion_movilidad, perfil_medico, imc)
                   VALUES (%s, %s, %s, %s)
                   ON DUPLICATE KEY UPDATE id_usuario = id_usuario""",
                (adulto_user_id, "Nivel: Reducida - Limitaciones: Rodilla delicada", "Perfil inicial.", 22.0),
            )
            cursor.execute("SELECT id FROM adulto_mayor WHERE id_usuario = %s", (adulto_user_id,))
            adulto_id = cursor.fetchone()["id"]

            cursor.execute(
                """INSERT INTO cuidador (id_usuario, cedula_medica, especialidad, id_tipo_cuidador)
                   VALUES (%s, %s, %s, %s)
                   ON DUPLICATE KEY UPDATE id_usuario = id_usuario""",
                (cuidador_user_id, "MED-0001", "Geriatría", 1),
            )

            cursor.execute(
                """INSERT INTO familiar (id_usuario)
                   VALUES (%s)
                   ON DUPLICATE KEY UPDATE id_usuario = id_usuario""",
                (familiar_user_id,),
            )
            cursor.execute("SELECT id FROM familiar WHERE id_usuario = %s", (familiar_user_id,))
            familiar_id = cursor.fetchone()["id"]

            cursor.execute(
                """INSERT INTO relaciones_familiar (id_familiar, id_adulto, autorizado)
                   VALUES (%s, %s, 1)
                   ON DUPLICATE KEY UPDATE autorizado = 1""",
                (familiar_id, adulto_id),
            )
            cursor.executemany(
                """INSERT INTO actividad (nombre, descripcion, id_tipo_actividad, nivel, impacto)
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
                """INSERT INTO antecedente_medico (nombre, descripcion) VALUES (%s, %s)
                   ON DUPLICATE KEY UPDATE nombre = VALUES(nombre)""",
                CATALOGO_ANTECEDENTES,
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
                (cuidador_user_id, "Recuerden realizar sus estiramientos matutinos.",
                 "Recuerden realizar sus estiramientos matutinos."),
            )
            cursor.execute(
                """INSERT INTO logros_usuario (id_usuario, id_logro)
                   SELECT %s, 1 FROM DUAL
                   WHERE NOT EXISTS (
                       SELECT 1 FROM logros_usuario WHERE id_usuario = %s AND id_logro = 1
                   )""",
                (adulto_user_id, adulto_user_id),
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

    def resumen_mongo(self, limite: int = 12) -> dict[str, Any]:
        """Devuelve un resumen administrativo, sin exponer identificadores internos."""
        if not self.mongo_ready or self.mongo_db is None:
            return {"disponible": False, "colecciones": []}
        resumen = []
        for nombre in ("estadisticas", "metricas", "sesiones", "telemetria"):
            try:
                coleccion = self.mongo_db[nombre]
                ejemplos = []
                for documento in coleccion.find({}, {"_id": 0}).sort("fecha", -1).limit(max(1, limite)):
                    ejemplos.append({
                        clave: str(valor)[:160]
                        for clave, valor in documento.items()
                        if clave not in {"usuario", "password", "password_hash", "correo"}
                    })
                resumen.append({"nombre": nombre, "total": coleccion.count_documents({}), "ejemplos": ejemplos})
            except PyMongoError:
                continue
        return {"disponible": True, "colecciones": resumen}

    def eliminar_datos_mongo_usuario(self, user_id: int) -> None:
        """Borra la telemetría asociada tras la eliminación voluntaria de la cuenta."""
        if not self.mongo_ready or self.mongo_db is None:
            return
        for nombre in ("estadisticas", "metricas", "sesiones", "telemetria"):
            try:
                self.mongo_db[nombre].delete_many({"usuario": user_id})
            except PyMongoError:
                pass

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
