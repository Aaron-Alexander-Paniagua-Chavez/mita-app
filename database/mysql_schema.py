"""Definición versionada del esquema MySQL de MITA.

Este módulo es la fuente de verdad de la estructura. El gestor de base de
datos lo ejecuta desde Python; el archivo ``schema.sql`` sólo queda como
referencia humana y nunca es necesario importarlo manualmente.
"""
from __future__ import annotations


SCHEMA_VERSION = 3


MYSQL_TABLE_DDL = (
    """
    CREATE TABLE IF NOT EXISTS schema_versions (
        version INT PRIMARY KEY,
        applied_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS usuarios (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nombre VARCHAR(150) NOT NULL,
        correo VARCHAR(254) NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        password_revealable VARBINARY(512) NULL,
        rol ENUM('Administrador', 'Adulto Mayor', 'Cuidador', 'Familiar') NOT NULL,
        fecha_registro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        UNIQUE KEY uk_usuarios_correo (correo),
        KEY idx_usuarios_rol (rol)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS adulto_mayor (
        id INT AUTO_INCREMENT PRIMARY KEY,
        id_usuario INT NOT NULL,
        fecha_nacimiento DATE NULL,
        limitaciones_movilidad VARCHAR(255) NOT NULL DEFAULT 'Ninguna',
        perfil_medico TEXT NULL,
        imc DECIMAL(5,2) NULL,
        nivel_movilidad VARCHAR(50) NOT NULL DEFAULT 'Normal',
        UNIQUE KEY uk_adulto_usuario (id_usuario),
        CONSTRAINT fk_adulto_usuario FOREIGN KEY (id_usuario)
            REFERENCES usuarios(id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS cuidador (
        id INT AUTO_INCREMENT PRIMARY KEY,
        id_usuario INT NOT NULL,
        cedula_medica VARCHAR(80) NULL,
        especialidad VARCHAR(120) NULL,
        UNIQUE KEY uk_cuidador_usuario (id_usuario),
        UNIQUE KEY uk_cuidador_cedula (cedula_medica),
        CONSTRAINT fk_cuidador_usuario FOREIGN KEY (id_usuario)
            REFERENCES usuarios(id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS actividad (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nombre VARCHAR(160) NOT NULL,
        descripcion TEXT NULL,
        tipo VARCHAR(50) NOT NULL,
        nivel TINYINT UNSIGNED NOT NULL DEFAULT 1,
        impacto VARCHAR(30) NULL,
        activa TINYINT(1) NOT NULL DEFAULT 1,
        UNIQUE KEY uk_actividad_nombre_tipo (nombre, tipo),
        KEY idx_actividad_tipo_nivel (tipo, nivel)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS alergia (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nombre VARCHAR(120) NOT NULL,
        descripcion TEXT NULL,
        UNIQUE KEY uk_alergia_nombre (nombre)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS adulto_alergia (
        id_adulto INT NOT NULL,
        id_alergia INT NOT NULL,
        observaciones VARCHAR(255) NULL,
        PRIMARY KEY (id_adulto, id_alergia),
        CONSTRAINT fk_adulto_alergia_adulto FOREIGN KEY (id_adulto)
            REFERENCES adulto_mayor(id) ON DELETE CASCADE,
        CONSTRAINT fk_adulto_alergia_alergia FOREIGN KEY (id_alergia)
            REFERENCES alergia(id) ON DELETE RESTRICT
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS antecedente_medico (
        id INT AUTO_INCREMENT PRIMARY KEY,
        id_adulto INT NOT NULL,
        nombre VARCHAR(150) NOT NULL,
        descripcion TEXT NULL,
        fecha_diagnostico DATE NULL,
        KEY idx_antecedente_adulto (id_adulto),
        CONSTRAINT fk_antecedente_adulto FOREIGN KEY (id_adulto)
            REFERENCES adulto_mayor(id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS habito (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nombre VARCHAR(120) NOT NULL,
        descripcion TEXT NULL,
        categoria VARCHAR(60) NULL,
        UNIQUE KEY uk_habito_nombre (nombre)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS adulto_habito (
        id_adulto INT NOT NULL,
        id_habito INT NOT NULL,
        frecuencia VARCHAR(80) NULL,
        PRIMARY KEY (id_adulto, id_habito),
        CONSTRAINT fk_adulto_habito_adulto FOREIGN KEY (id_adulto)
            REFERENCES adulto_mayor(id) ON DELETE CASCADE,
        CONSTRAINT fk_adulto_habito_habito FOREIGN KEY (id_habito)
            REFERENCES habito(id) ON DELETE RESTRICT
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS dificultad_cognitiva (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nombre VARCHAR(120) NOT NULL,
        descripcion TEXT NULL,
        UNIQUE KEY uk_dificultad_nombre (nombre)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS adulto_dificultad (
        id_adulto INT NOT NULL,
        id_dificultad INT NOT NULL,
        nivel VARCHAR(50) NULL,
        PRIMARY KEY (id_adulto, id_dificultad),
        CONSTRAINT fk_adulto_dificultad_adulto FOREIGN KEY (id_adulto)
            REFERENCES adulto_mayor(id) ON DELETE CASCADE,
        CONSTRAINT fk_adulto_dificultad_dificultad FOREIGN KEY (id_dificultad)
            REFERENCES dificultad_cognitiva(id) ON DELETE RESTRICT
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS medicamento (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nombre VARCHAR(150) NOT NULL,
        presentacion VARCHAR(120) NULL,
        indicaciones TEXT NULL,
        UNIQUE KEY uk_medicamento_nombre_presentacion (nombre, presentacion)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS tratamiento (
        id INT AUTO_INCREMENT PRIMARY KEY,
        id_adulto INT NOT NULL,
        id_medicamento INT NOT NULL,
        id_cuidador INT NULL,
        dosis VARCHAR(100) NOT NULL,
        frecuencia VARCHAR(100) NOT NULL,
        fecha_inicio DATE NULL,
        fecha_fin DATE NULL,
        activo TINYINT(1) NOT NULL DEFAULT 1,
        KEY idx_tratamiento_adulto_activo (id_adulto, activo),
        CONSTRAINT fk_tratamiento_adulto FOREIGN KEY (id_adulto)
            REFERENCES adulto_mayor(id) ON DELETE CASCADE,
        CONSTRAINT fk_tratamiento_medicamento FOREIGN KEY (id_medicamento)
            REFERENCES medicamento(id) ON DELETE RESTRICT,
        CONSTRAINT fk_tratamiento_cuidador FOREIGN KEY (id_cuidador)
            REFERENCES cuidador(id) ON DELETE SET NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS registro_toma (
        id INT AUTO_INCREMENT PRIMARY KEY,
        id_tratamiento INT NOT NULL,
        fecha_hora DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        tomado TINYINT(1) NOT NULL,
        observaciones VARCHAR(255) NULL,
        KEY idx_registro_toma_tratamiento_fecha (id_tratamiento, fecha_hora),
        CONSTRAINT fk_registro_toma_tratamiento FOREIGN KEY (id_tratamiento)
            REFERENCES tratamiento(id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS metrica_biometrica (
        id INT AUTO_INCREMENT PRIMARY KEY,
        id_adulto INT NOT NULL,
        tipo VARCHAR(80) NOT NULL,
        valor DECIMAL(10,2) NOT NULL,
        unidad VARCHAR(30) NULL,
        fecha_hora DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        KEY idx_metrica_adulto_fecha (id_adulto, fecha_hora),
        CONSTRAINT fk_metrica_adulto FOREIGN KEY (id_adulto)
            REFERENCES adulto_mayor(id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS progreso (
        id_usuario INT PRIMARY KEY,
        puntos INT NOT NULL DEFAULT 0,
        racha_dias INT NOT NULL DEFAULT 0,
        actividades_completadas INT NOT NULL DEFAULT 0,
        cognitivas_completadas INT NOT NULL DEFAULT 0,
        ultima_actividad DATETIME NULL,
        CONSTRAINT fk_progreso_usuario FOREIGN KEY (id_usuario)
            REFERENCES usuarios(id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS publicaciones (
        id INT AUTO_INCREMENT PRIMARY KEY,
        id_autor INT NOT NULL,
        contenido TEXT NOT NULL,
        fecha_hora DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        estado ENUM('visible', 'oculta', 'eliminada') NOT NULL DEFAULT 'visible',
        KEY idx_publicaciones_estado_fecha (estado, fecha_hora),
        CONSTRAINT fk_publicaciones_autor FOREIGN KEY (id_autor)
            REFERENCES usuarios(id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS actividades_historial (
        id INT AUTO_INCREMENT PRIMARY KEY,
        id_usuario INT NOT NULL,
        id_actividad INT NULL,
        tipo_actividad VARCHAR(50) NOT NULL,
        titulo VARCHAR(200) NOT NULL,
        puntos INT NOT NULL DEFAULT 0,
        fecha_hora DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        KEY idx_historial_usuario_fecha (id_usuario, fecha_hora),
        CONSTRAINT fk_historial_usuario FOREIGN KEY (id_usuario)
            REFERENCES usuarios(id) ON DELETE CASCADE,
        CONSTRAINT fk_historial_actividad FOREIGN KEY (id_actividad)
            REFERENCES actividad(id) ON DELETE SET NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS logros_usuario (
        id INT AUTO_INCREMENT PRIMARY KEY,
        id_usuario INT NOT NULL,
        id_logro VARCHAR(50) NOT NULL,
        desbloqueado_en DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        UNIQUE KEY uk_usuario_logro (id_usuario, id_logro),
        CONSTRAINT fk_logro_usuario FOREIGN KEY (id_usuario)
            REFERENCES usuarios(id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS auditoria (
        id INT AUTO_INCREMENT PRIMARY KEY,
        accion VARCHAR(100) NOT NULL,
        detalle TEXT NULL,
        id_admin INT NULL,
        fecha_hora DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        KEY idx_auditoria_fecha (fecha_hora),
        CONSTRAINT fk_auditoria_admin FOREIGN KEY (id_admin)
            REFERENCES usuarios(id) ON DELETE SET NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS relaciones_familiar (
        id INT AUTO_INCREMENT PRIMARY KEY,
        id_familiar INT NOT NULL,
        id_adulto INT NOT NULL,
        autorizado TINYINT(1) NOT NULL DEFAULT 1,
        fecha_vinculo DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        UNIQUE KEY uk_familiar_adulto (id_familiar, id_adulto),
        KEY idx_relacion_adulto (id_adulto),
        CONSTRAINT fk_relacion_familiar FOREIGN KEY (id_familiar)
            REFERENCES usuarios(id) ON DELETE CASCADE,
        CONSTRAINT fk_relacion_adulto FOREIGN KEY (id_adulto)
            REFERENCES usuarios(id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS migraciones_legacy (
        id INT AUTO_INCREMENT PRIMARY KEY,
        base_origen VARCHAR(64) NOT NULL,
        ejecutada_en DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        usuarios_migrados INT NOT NULL DEFAULT 0,
        incidencias TEXT NULL,
        UNIQUE KEY uk_migracion_origen (base_origen)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS conversaciones (
        id INT AUTO_INCREMENT PRIMARY KEY,
        tipo ENUM('directa', 'grupo') NOT NULL DEFAULT 'directa',
        titulo VARCHAR(160) NULL,
        creada_en DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        KEY idx_conversaciones_tipo (tipo)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS conversacion_participantes (
        id_conversacion INT NOT NULL,
        id_usuario INT NOT NULL,
        puede_compartir_progreso TINYINT(1) NOT NULL DEFAULT 0,
        unido_en DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (id_conversacion, id_usuario),
        CONSTRAINT fk_participante_conversacion FOREIGN KEY (id_conversacion)
            REFERENCES conversaciones(id) ON DELETE CASCADE,
        CONSTRAINT fk_participante_usuario FOREIGN KEY (id_usuario)
            REFERENCES usuarios(id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS mensajes (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        id_conversacion INT NOT NULL,
        id_remitente INT NOT NULL,
        contenido TEXT NOT NULL,
        tipo ENUM('texto', 'reporte') NOT NULL DEFAULT 'texto',
        enviado_en DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        eliminado_en DATETIME NULL,
        KEY idx_mensajes_conversacion_fecha (id_conversacion, enviado_en),
        CONSTRAINT fk_mensaje_conversacion FOREIGN KEY (id_conversacion)
            REFERENCES conversaciones(id) ON DELETE CASCADE,
        CONSTRAINT fk_mensaje_remitente FOREIGN KEY (id_remitente)
            REFERENCES usuarios(id) ON DELETE RESTRICT
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS mensaje_destinatarios (
        id_mensaje BIGINT NOT NULL,
        id_usuario INT NOT NULL,
        leido_en DATETIME NULL,
        PRIMARY KEY (id_mensaje, id_usuario),
        CONSTRAINT fk_destinatario_mensaje FOREIGN KEY (id_mensaje)
            REFERENCES mensajes(id) ON DELETE CASCADE,
        CONSTRAINT fk_destinatario_usuario FOREIGN KEY (id_usuario)
            REFERENCES usuarios(id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS reportes_progreso (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        id_adulto INT NOT NULL,
        id_creado_por INT NOT NULL,
        resumen JSON NOT NULL,
        periodo_desde DATE NULL,
        periodo_hasta DATE NULL,
        creado_en DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        KEY idx_reportes_adulto_fecha (id_adulto, creado_en),
        CONSTRAINT fk_reporte_adulto FOREIGN KEY (id_adulto)
            REFERENCES usuarios(id) ON DELETE CASCADE,
        CONSTRAINT fk_reporte_creador FOREIGN KEY (id_creado_por)
            REFERENCES usuarios(id) ON DELETE RESTRICT
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS reporte_destinatarios (
        id_reporte BIGINT NOT NULL,
        id_usuario INT NOT NULL,
        permiso ENUM('ver', 'descargar') NOT NULL DEFAULT 'ver',
        compartido_en DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        revocado_en DATETIME NULL,
        PRIMARY KEY (id_reporte, id_usuario),
        CONSTRAINT fk_reporte_destinatario FOREIGN KEY (id_reporte)
            REFERENCES reportes_progreso(id) ON DELETE CASCADE,
        CONSTRAINT fk_reporte_destinatario_usuario FOREIGN KEY (id_usuario)
            REFERENCES usuarios(id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    # v3: columna para que solo el dueño (con clave maestra) pueda descifrar y ver
    # la contraseña original de cada usuario. Se conserva el hash PBKDF2 para
    # que el inicio de sesión normal no dependa nunca del dueño.
    """
    ALTER TABLE usuarios ADD COLUMN password_revealable VARBINARY(512) NULL
    """,
)


CATALOGO_ACTIVIDADES = (
    ("Estiramiento de brazos", "Rutina física de bajo impacto.", "fisico", 1, "Bajo"),
    ("Caminata ligera guiada", "Caminata adaptada de cinco minutos.", "fisico", 1, "Bajo"),
    ("Juego de memoria", "Actividad de asociación de cartas.", "cognitivo", 1, "Bajo"),
    ("Secuencias numéricas", "Estimulación de atención y memoria.", "cognitivo", 3, "Bajo"),
)

CATALOGO_ALERGIAS = (
    ("Ninguna conocida", "Sin alergias registradas."),
    ("Penicilina", "Alergia a antibióticos de la familia penicilina."),
    ("Látex", "Sensibilidad al látex."),
)

CATALOGO_HABITOS = (
    ("Hidratación", "Registrar consumo de agua.", "bienestar"),
    ("Caminata diaria", "Actividad física suave.", "actividad"),
    ("Sueño regular", "Mantener horario de descanso.", "descanso"),
)

CATALOGO_DIFICULTADES = (
    ("Memoria", "Dificultad para recordar información reciente."),
    ("Atención", "Dificultad para mantener la concentración."),
)

CATALOGO_MEDICAMENTOS = (
    ("Paracetamol", "Tableta", "Usar únicamente bajo indicación profesional."),
    ("Losartán", "Tableta", "Usar únicamente bajo indicación profesional."),
)
