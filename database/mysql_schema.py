from __future__ import annotations

CATALOGO_ESTADO_TOMA = (
    (1, "Programado", "Toma de medicamento agendada"),
    (2, "Tomado", "Medicamento ingerido a tiempo"),
    (3, "Omitido", "Toma omitida por el usuario o indicación"),
    (4, "Atrasado", "Toma realizada fuera del horario programado"),
)

CATALOGO_TIPO_ACTIVIDAD = (
    (1, "Física", "Ejercicios y rutinas de movimiento físico"),
    (2, "Cognitiva", "Ejercicios de estimulación cognitiva y memoria"),
)

CATALOGO_TIPO_CUIDADOR = (
    (1, "Médico", "Profesional médico especialista"),
    (2, "Enfermero", "Personal de enfermería y atención directa"),
    (3, "Terapeuta", "Terapeuta físico o ocupacional"),
    (4, "Cuidador formal", "Cuidador primario capacitado"),
)

CATALOGO_LOGROS = (
    (1, "primer_dia", "Primer Día", "Iniciaste tu camino en MITA", 10),
    (2, "racha_3", "Constancia 3 Días", "Completaste actividades 3 días seguidos", 30),
    (3, "mente_activa", "Mente Activa", "Completaste 5 actividades cognitivas", 50),
    (4, "cuerpo_sano", "Cuerpo en Movimiento", "Completaste 5 actividades físicas", 50),
)

# Catálogo de tipos de métrica biométrica.
# Cada entrada: (id_tipo_metrica, nombre, unidad_estandar, descripcion)
CATALOGO_TIPO_METRICA = (
    (1, "Frecuencia Cardíaca", "bpm",     "Pulsaciones cardíacas por minuto"),
    (2, "Peso",               "kg",      "Masa corporal en kilogramos"),
    (3, "Saturación de Oxígeno", "%",    "SpO2: porcentaje de saturación de oxígeno en sangre"),
    (4, "Pasos",              "pasos",   "Número de pasos caminados"),
    (5, "Sueño",              "minutos", "Duración del período de sueño en minutos"),
)

MYSQL_TABLE_DDL = (
    """
    CREATE TABLE IF NOT EXISTS usuarios (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nombre VARCHAR(150) NOT NULL,
        correo VARCHAR(254) NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        rol ENUM('Administrador', 'Adulto Mayor', 'Cuidador', 'Familiar') NOT NULL,
        genero VARCHAR(30) NULL,
        telefono VARCHAR(20) NULL,
        ubicacion VARCHAR(200) NULL,
        foto_perfil VARCHAR(500) NULL,
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
        descripcion_movilidad TEXT NULL,
        perfil_medico TEXT NULL,
        descripcion_habitos TEXT NULL,
        imc DECIMAL(5,2) NULL,
        UNIQUE KEY uk_adulto_usuario (id_usuario),
        CONSTRAINT fk_adulto_usuario FOREIGN KEY (id_usuario)
            REFERENCES usuarios(id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS tipo_cuidador (
        id_tipo_cuidador INT AUTO_INCREMENT PRIMARY KEY,
        nombre VARCHAR(80) NOT NULL,
        descripcion TEXT NULL,
        UNIQUE KEY uk_tipo_cuidador_nombre (nombre)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS cuidador (
        id INT AUTO_INCREMENT PRIMARY KEY,
        id_usuario INT NOT NULL,
        cedula_medica VARCHAR(80) NULL,
        especialidad VARCHAR(120) NULL,
        id_tipo_cuidador INT NULL,
        UNIQUE KEY uk_cuidador_usuario (id_usuario),
        UNIQUE KEY uk_cuidador_cedula (cedula_medica),
        CONSTRAINT fk_cuidador_usuario FOREIGN KEY (id_usuario)
            REFERENCES usuarios(id) ON DELETE CASCADE,
        CONSTRAINT fk_cuidador_tipo FOREIGN KEY (id_tipo_cuidador)
            REFERENCES tipo_cuidador(id_tipo_cuidador) ON DELETE SET NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS adulto_cuidador (
        id INT AUTO_INCREMENT PRIMARY KEY,
        id_adulto INT NOT NULL,
        id_cuidador INT NOT NULL,
        fecha_vinculo DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        activo TINYINT(1) NOT NULL DEFAULT 1,
        observaciones TEXT NULL,

        UNIQUE KEY uk_adulto_cuidador (id_adulto, id_cuidador),

        CONSTRAINT fk_adulto_cuidador_adulto
            FOREIGN KEY (id_adulto)
            REFERENCES adulto_mayor(id)
            ON DELETE CASCADE,

        CONSTRAINT fk_adulto_cuidador_cuidador
            FOREIGN KEY (id_cuidador)
            REFERENCES cuidador(id)
            ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS tipo_actividad (
        id_tipo_actividad INT AUTO_INCREMENT PRIMARY KEY,
        nombre VARCHAR(50) NOT NULL,
        descripcion TEXT NULL,
        UNIQUE KEY uk_tipo_actividad_nombre (nombre)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS actividad (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nombre VARCHAR(160) NOT NULL,
        descripcion TEXT NULL,
        id_tipo_actividad INT NOT NULL DEFAULT 1,
        nivel TINYINT UNSIGNED NOT NULL DEFAULT 1,
        impacto VARCHAR(30) NULL,
        activa TINYINT(1) NOT NULL DEFAULT 1,
        UNIQUE KEY uk_actividad_nombre_tipo (nombre, id_tipo_actividad),
        KEY idx_actividad_tipo_nivel (id_tipo_actividad, nivel),
        CONSTRAINT fk_actividad_tipo FOREIGN KEY (id_tipo_actividad)
            REFERENCES tipo_actividad(id_tipo_actividad) ON DELETE RESTRICT
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
        nombre VARCHAR(150) NOT NULL,
        descripcion TEXT NULL,
        UNIQUE KEY uk_antecedente_nombre (nombre)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS adulto_antecedente (
        id_adulto INT NOT NULL,
        id_antecedente INT NOT NULL,
        observaciones VARCHAR(255) NULL,
        PRIMARY KEY (id_adulto, id_antecedente),
        CONSTRAINT fk_adulto_antecedente_adulto FOREIGN KEY (id_adulto)
            REFERENCES adulto_mayor(id) ON DELETE CASCADE,
        CONSTRAINT fk_adulto_antecedente_antecedente FOREIGN KEY (id_antecedente)
            REFERENCES antecedente_medico(id) ON DELETE RESTRICT
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
    CREATE TABLE IF NOT EXISTS estado_toma (
        id_estado INT AUTO_INCREMENT PRIMARY KEY,
        nombre VARCHAR(50) NOT NULL,
        descripcion TEXT NULL,
        UNIQUE KEY uk_estado_toma_nombre (nombre)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS registro_toma (
        id INT AUTO_INCREMENT PRIMARY KEY,
        id_tratamiento INT NOT NULL,
        fecha_hora DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        id_estado INT NOT NULL DEFAULT 1,
        hora_programada TIME NULL,
        hora_real DATETIME NULL,
        observaciones VARCHAR(255) NULL,
        KEY idx_registro_toma_tratamiento_fecha (id_tratamiento, fecha_hora),
        CONSTRAINT fk_registro_toma_tratamiento FOREIGN KEY (id_tratamiento)
            REFERENCES tratamiento(id) ON DELETE CASCADE,
        CONSTRAINT fk_registro_toma_estado FOREIGN KEY (id_estado)
            REFERENCES estado_toma(id_estado) ON DELETE RESTRICT
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS registro_actividad (
        id INT AUTO_INCREMENT PRIMARY KEY,
        id_usuario INT NOT NULL,
        id_actividad INT NULL,
        fecha DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        hora_inicio DATETIME NULL,
        hora_fin DATETIME NULL,
        nivel_alcanzado TINYINT NULL,
        desempeno VARCHAR(50) NULL,
        puntos INT NOT NULL DEFAULT 0,
        observaciones TEXT NULL,
        KEY idx_registro_actividad_usuario_fecha (id_usuario, fecha),
        CONSTRAINT fk_registro_actividad_usuario FOREIGN KEY (id_usuario)
            REFERENCES usuarios(id) ON DELETE CASCADE,
        CONSTRAINT fk_registro_actividad_actividad FOREIGN KEY (id_actividad)
            REFERENCES actividad(id) ON DELETE SET NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS familiar (
        id INT AUTO_INCREMENT PRIMARY KEY,
        id_usuario INT NOT NULL,
        UNIQUE KEY uk_familiar_usuario (id_usuario),
        CONSTRAINT fk_familiar_usuario FOREIGN KEY (id_usuario)
            REFERENCES usuarios(id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS relaciones_familiar (
        id INT AUTO_INCREMENT PRIMARY KEY,
        id_familiar INT NOT NULL,
        id_adulto INT NOT NULL,
        tipo_relacion VARCHAR(80) NULL,
        autorizado TINYINT(1) NOT NULL DEFAULT 1,
        fecha_vinculo DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        UNIQUE KEY uk_familiar_adulto (id_familiar, id_adulto),
        KEY idx_relacion_adulto (id_adulto),
        CONSTRAINT fk_relacion_familiar FOREIGN KEY (id_familiar)
            REFERENCES familiar(id) ON DELETE CASCADE,
        CONSTRAINT fk_relacion_adulto FOREIGN KEY (id_adulto)
            REFERENCES adulto_mayor(id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS dieta_adulto (
        id INT AUTO_INCREMENT PRIMARY KEY,
        id_adulto INT NOT NULL,
        tipo_dieta VARCHAR(100) NULL,
        descripcion TEXT NULL,
        fecha_inicio DATE NULL,
        fecha_fin DATE NULL,
        activa TINYINT(1) NOT NULL DEFAULT 1,
        KEY idx_dieta_adulto (id_adulto, activa),
        CONSTRAINT fk_dieta_adulto FOREIGN KEY (id_adulto)
            REFERENCES adulto_mayor(id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS registro_sueno (
        id INT AUTO_INCREMENT PRIMARY KEY,
        id_adulto INT NOT NULL,
        fecha DATE NOT NULL,
        hora_inicio TIME NULL,
        hora_fin TIME NULL,
        duracion_minutos INT NULL,
        calidad VARCHAR(50) NULL,
        observaciones TEXT NULL,
        KEY idx_registro_sueno_adulto_fecha (id_adulto, fecha),
        CONSTRAINT fk_registro_sueno_adulto FOREIGN KEY (id_adulto)
            REFERENCES adulto_mayor(id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS logro (
        id INT AUTO_INCREMENT PRIMARY KEY,
        codigo VARCHAR(50) NOT NULL,
        nombre VARCHAR(120) NOT NULL,
        descripcion TEXT NULL,
        puntos INT NOT NULL DEFAULT 0,
        UNIQUE KEY uk_logro_codigo (codigo)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS logros_usuario (
        id INT AUTO_INCREMENT PRIMARY KEY,
        id_usuario INT NOT NULL,
        id_logro INT NOT NULL,
        desbloqueado_en DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        UNIQUE KEY uk_usuario_logro (id_usuario, id_logro),
        CONSTRAINT fk_logro_usuario FOREIGN KEY (id_usuario)
            REFERENCES usuarios(id) ON DELETE CASCADE,
        CONSTRAINT fk_logros_usuario_logro FOREIGN KEY (id_logro)
            REFERENCES logro(id) ON DELETE RESTRICT
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS notificacion (
        id INT AUTO_INCREMENT PRIMARY KEY,
        id_usuario INT NOT NULL,
        id_registro_toma INT NULL,
        tipo VARCHAR(50) NOT NULL,
        mensaje TEXT NOT NULL,
        fecha_programada DATETIME NOT NULL,
        fecha_enviada DATETIME NULL,
        estado ENUM('Pendiente', 'Enviado', 'Leido', 'Cancelado') NOT NULL DEFAULT 'Pendiente',
        KEY idx_notificacion_usuario_estado (id_usuario, estado),
        CONSTRAINT fk_notificacion_usuario FOREIGN KEY (id_usuario)
            REFERENCES usuarios(id) ON DELETE CASCADE,
        CONSTRAINT fk_notificacion_registro_toma FOREIGN KEY (id_registro_toma)
            REFERENCES registro_toma(id) ON DELETE SET NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS tipo_metrica (
        id_tipo_metrica INT AUTO_INCREMENT PRIMARY KEY,
        nombre VARCHAR(80) NOT NULL UNIQUE,
        unidad_estandar VARCHAR(30) NULL,
        descripcion TEXT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS metrica_biometrica (
        id INT AUTO_INCREMENT PRIMARY KEY,
        id_adulto INT NOT NULL,
        id_tipo_metrica INT NOT NULL,
        valor DECIMAL(10,2) NOT NULL,
        unidad VARCHAR(30) NULL,
        fecha_hora DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        KEY idx_metrica_adulto_fecha (id_adulto, fecha_hora),
        CONSTRAINT fk_metrica_adulto FOREIGN KEY (id_adulto)
            REFERENCES adulto_mayor(id) ON DELETE CASCADE,
        CONSTRAINT fk_metrica_tipo FOREIGN KEY (id_tipo_metrica)
            REFERENCES tipo_metrica(id_tipo_metrica) ON DELETE RESTRICT
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
    CREATE TABLE IF NOT EXISTS contacto_emergencia (
        id INT AUTO_INCREMENT PRIMARY KEY,
        id_adulto INT NOT NULL,
        nombre VARCHAR(150) NOT NULL,
        telefono VARCHAR(20) NOT NULL,
        relacion VARCHAR(80) NULL,
        CONSTRAINT fk_contacto_adulto FOREIGN KEY (id_adulto)
            REFERENCES adulto_mayor(id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS preferencias_usuario (
        id_usuario INT PRIMARY KEY,
        preferencias JSON NOT NULL,
        actualizado_en DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            ON UPDATE CURRENT_TIMESTAMP,
        CONSTRAINT fk_preferencias_usuario FOREIGN KEY (id_usuario)
            REFERENCES usuarios(id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS sesiones_uso (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        id_usuario INT NOT NULL,
        inicio DATETIME NOT NULL,
        fin DATETIME NOT NULL,
        duracion_segundos INT UNSIGNED NOT NULL DEFAULT 0,
        KEY idx_sesiones_uso_usuario_inicio (id_usuario, inicio),
        CONSTRAINT fk_sesiones_uso_usuario FOREIGN KEY (id_usuario)
            REFERENCES usuarios(id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
    """
    CREATE TABLE IF NOT EXISTS tiempos_actividad (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        id_usuario INT NOT NULL,
        titulo VARCHAR(200) NOT NULL,
        categoria VARCHAR(50) NOT NULL,
        duracion_segundos INT UNSIGNED NOT NULL DEFAULT 0,
        fecha_hora DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        KEY idx_tiempos_actividad_usuario_fecha (id_usuario, fecha_hora),
        CONSTRAINT fk_tiempos_actividad_usuario FOREIGN KEY (id_usuario)
            REFERENCES usuarios(id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """,
)

MYSQL_VIEWS_DDL = (
    """
    CREATE OR REPLACE VIEW vw_adherencia_medicacion AS
    SELECT 
        am.id AS id_adulto,
        u.nombre AS nombre_adulto,
        m.nombre AS medicamento,
        t.id AS id_tratamiento,
        COUNT(rt.id) AS tomas_totales,
        SUM(CASE WHEN et.nombre = 'Tomado' THEN 1 ELSE 0 END) AS tomas_tomadas,
        SUM(CASE WHEN et.nombre = 'Omitido' THEN 1 ELSE 0 END) AS tomas_omitidas,
        SUM(CASE WHEN et.nombre = 'Atrasado' THEN 1 ELSE 0 END) AS tomas_atrasadas,
        SUM(CASE WHEN et.nombre = 'Programado' THEN 1 ELSE 0 END) AS tomas_programadas,
        ROUND(
            COALESCE(
                (SUM(CASE WHEN et.nombre IN ('Tomado', 'Atrasado') THEN 1 ELSE 0 END) / NULLIF(COUNT(rt.id), 0)) * 100,
                0
            ), 2
        ) AS porcentaje_adherencia
    FROM adulto_mayor am
    JOIN usuarios u ON am.id_usuario = u.id
    JOIN tratamiento t ON t.id_adulto = am.id
    JOIN medicamento m ON t.id_medicamento = m.id
    LEFT JOIN registro_toma rt ON rt.id_tratamiento = t.id
    LEFT JOIN estado_toma et ON rt.id_estado = et.id_estado
    GROUP BY am.id, u.nombre, m.nombre, t.id
    """,
    """
    CREATE OR REPLACE VIEW vw_progreso AS
    SELECT 
        u.id AS id_usuario,
        u.nombre AS nombre_usuario,
        COALESCE(SUM(ra.puntos), 0) AS puntos,
        COUNT(ra.id) AS actividades_completadas,
        SUM(CASE WHEN ta.nombre = 'Cognitiva' THEN 1 ELSE 0 END) AS cognitivas_completadas,
        SUM(CASE WHEN ta.nombre = 'Física' THEN 1 ELSE 0 END) AS fisicas_completadas,
        MAX(ra.fecha) AS ultima_actividad
    FROM usuarios u
    LEFT JOIN registro_actividad ra ON ra.id_usuario = u.id
    LEFT JOIN actividad a ON ra.id_actividad = a.id
    LEFT JOIN tipo_actividad ta ON a.id_tipo_actividad = ta.id_tipo_actividad
    GROUP BY u.id, u.nombre
    """,
)

CATALOGO_ACTIVIDADES = (
    ("Estiramiento de brazos", "Rutina física de bajo impacto.", 1, 1, "Bajo"),
    ("Caminata ligera guiada", "Caminata adaptada de cinco minutos.", 1, 1, "Bajo"),
    ("Respiración consciente", "Respiración suave sentado.", 1, 1, "Bajo"),
    ("Movilidad de hombros", "Movimientos lentos de hombros.", 1, 1, "Bajo"),
    ("Manos activas", "Apertura y cierre de manos sentado.", 1, 1, "Bajo"),
    ("Estiramiento de cuello", "Movilidad cervical suave.", 1, 1, "Bajo"),
    ("Postura sentada", "Alineación y respiración en silla.", 1, 1, "Bajo"),
    ("Baile sentado", "Ritmo suave desde una silla.", 1, 2, "Bajo"),
    ("Elevación de talones", "Fortalecimiento de tobillos con apoyo.", 1, 2, "Bajo"),
    ("Paso lateral con apoyo", "Desplazamiento corto junto a una silla.", 1, 2, "Medio"),
    ("Equilibrio con respaldo", "Equilibrio de pie con silla estable.", 1, 2, "Medio"),
    ("Sentarse y levantarse", "Movimiento funcional con silla estable.", 1, 3, "Medio"),
    ("Caminata por intervalos", "Paseo con descansos programados.", 1, 3, "Medio"),
    ("Estiramiento de pantorrilla", "Estiramiento leve con apoyo.", 1, 2, "Bajo"),
    ("Movilidad de tobillos", "Círculos suaves de tobillos sentado.", 1, 1, "Bajo"),
    ("Tai chi básico", "Secuencia lenta de brazos y postura.", 1, 2, "Bajo"),
    ("Juego de memoria", "Actividad de asociación de cartas.", 2, 1, "Bajo"),
    ("Secuencias numéricas", "Estimulación de atención y memoria.", 2, 3, "Bajo"),
    ("Buscar diferencias", "Atención visual entre dos escenas.", 2, 1, "Bajo"),
    ("Palabras por categoría", "Lenguaje y asociación de ideas.", 2, 1, "Bajo"),
    ("Sopa de letras suave", "Búsqueda visual sin límite de tiempo.", 2, 2, "Bajo"),
    ("Rompecabezas de figuras", "Organización visual paso a paso.", 2, 2, "Bajo"),
    ("Cálculo cotidiano", "Operaciones sencillas de la vida diaria.", 2, 2, "Bajo"),
    ("Ordenar una historia", "Secuenciar imágenes o frases.", 2, 2, "Bajo"),
    ("Atención a sonidos", "Reconocer patrones de sonidos cotidianos.", 2, 1, "Bajo"),
    ("Orientación del día", "Práctica de fecha, clima y rutina.", 2, 1, "Bajo"),
    ("Reconocer emociones", "Identificar emociones en expresiones.", 2, 1, "Bajo"),
    ("Nombres y lugares", "Evocar categorías familiares con apoyo.", 2, 2, "Bajo"),
    ("Patrones de colores", "Completar patrones visuales suaves.", 2, 2, "Bajo"),
    ("Lectura acompañada", "Comprensión de un texto breve.", 2, 1, "Bajo"),
    ("Planificar una receta", "Secuencia práctica de pasos cotidianos.", 2, 2, "Bajo"),
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

CATALOGO_ANTECEDENTES = (
    ("Hipertensión", "Presión arterial alta crónica."),
    ("Diabetes Tipo 2", "Nivel alto de azúcar en la sangre."),
    ("Artritis", "Inflamación de las articulaciones."),
)

CATALOGO_MEDICAMENTOS = (
    ("Paracetamol", "Tableta", "Usar únicamente bajo indicación profesional."),
    ("Losartán", "Tableta", "Usar únicamente bajo indicación profesional."),
)
