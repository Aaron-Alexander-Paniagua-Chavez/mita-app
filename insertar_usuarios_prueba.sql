USE SistemaGeriatrico;

START TRANSACTION;

-- =========================================================
-- 1. LIMPIAR SOLAMENTE USUARIOS DE PRUEBA
-- =========================================================

DELETE FROM usuarios
WHERE correo LIKE 'admin_prueba_%@mita.test'
   OR correo LIKE 'adulto_prueba_%@mita.test'
   OR correo LIKE 'cuidador_prueba_%@mita.test'
   OR correo LIKE 'familiar_prueba_%@mita.test';


-- =========================================================
-- 2. OBTENER UN PASSWORD_HASH REAL Y COMPATIBLE
-- =========================================================

SET @password_hash = (
    SELECT password_hash
    FROM usuarios
    WHERE correo = 'admin@mita.local'
    LIMIT 1
);

-- Comprobación de seguridad:
-- si no existe admin@mita.local, detener la ejecución.
SELECT
    CASE
        WHEN @password_hash IS NULL THEN
            'ERROR: no existe admin@mita.local'
        ELSE
            'OK: password_hash obtenido'
    END AS estado_hash;


-- =========================================================
-- 3. ADMINISTRADORES (10)
-- =========================================================

INSERT INTO usuarios
(
    nombre,
    correo,
    password_hash,
    rol,
    genero,
    telefono,
    ubicacion,
    foto_perfil
)
WITH RECURSIVE numeros AS (
    SELECT 1 AS n
    UNION ALL
    SELECT n + 1
    FROM numeros
    WHERE n < 10
)
SELECT
    CONCAT('Administrador Prueba ', LPAD(n, 2, '0')),
    CONCAT('admin_prueba_', LPAD(n, 2, '0'), '@mita.test'),
    @password_hash,
    'Administrador',
    CASE WHEN MOD(n, 2) = 0 THEN 'Femenino' ELSE 'Masculino' END,
    CONCAT('555100', LPAD(n, 2, '0')),
    CONCAT('Ciudad de Prueba ', n),
    NULL
FROM numeros;


-- =========================================================
-- 4. ADULTOS MAYORES (30)
-- =========================================================

INSERT INTO usuarios
(
    nombre,
    correo,
    password_hash,
    rol,
    genero,
    telefono,
    ubicacion,
    foto_perfil
)
WITH RECURSIVE numeros AS (
    SELECT 1 AS n
    UNION ALL
    SELECT n + 1
    FROM numeros
    WHERE n < 30
)
SELECT
    CONCAT('Adulto Mayor Prueba ', LPAD(n, 2, '0')),
    CONCAT('adulto_prueba_', LPAD(n, 2, '0'), '@mita.test'),
    @password_hash,
    'Adulto Mayor',
    CASE WHEN MOD(n, 2) = 0 THEN 'Femenino' ELSE 'Masculino' END,
    CONCAT('555200', LPAD(n, 2, '0')),
    CONCAT('Ciudad de Prueba ', n),
    NULL
FROM numeros;


-- =========================================================
-- 5. CUIDADORES (30)
-- =========================================================

INSERT INTO usuarios
(
    nombre,
    correo,
    password_hash,
    rol,
    genero,
    telefono,
    ubicacion,
    foto_perfil
)
WITH RECURSIVE numeros AS (
    SELECT 1 AS n
    UNION ALL
    SELECT n + 1
    FROM numeros
    WHERE n < 30
)
SELECT
    CONCAT('Cuidador Prueba ', LPAD(n, 2, '0')),
    CONCAT('cuidador_prueba_', LPAD(n, 2, '0'), '@mita.test'),
    @password_hash,
    'Cuidador',
    CASE WHEN MOD(n, 2) = 0 THEN 'Femenino' ELSE 'Masculino' END,
    CONCAT('555300', LPAD(n, 2, '0')),
    CONCAT('Ciudad de Prueba ', n),
    NULL
FROM numeros;


-- =========================================================
-- 6. FAMILIARES (30)
-- =========================================================

INSERT INTO usuarios
(
    nombre,
    correo,
    password_hash,
    rol,
    genero,
    telefono,
    ubicacion,
    foto_perfil
)
WITH RECURSIVE numeros AS (
    SELECT 1 AS n
    UNION ALL
    SELECT n + 1
    FROM numeros
    WHERE n < 30
)
SELECT
    CONCAT('Familiar Prueba ', LPAD(n, 2, '0')),
    CONCAT('familiar_prueba_', LPAD(n, 2, '0'), '@mita.test'),
    @password_hash,
    'Familiar',
    CASE WHEN MOD(n, 2) = 0 THEN 'Femenino' ELSE 'Masculino' END,
    CONCAT('555400', LPAD(n, 2, '0')),
    CONCAT('Ciudad de Prueba ', n),
    NULL
FROM numeros;


-- =========================================================
-- 7. CREAR PERFIL DE ADULTO MAYOR
-- =========================================================

INSERT INTO adulto_mayor
(
    id_usuario,
    fecha_nacimiento,
    descripcion_movilidad,
    perfil_medico,
    descripcion_habitos,
    imc
)
SELECT
    u.id,
    DATE_SUB(CURDATE(), INTERVAL (65 + MOD(u.id, 25)) YEAR),
    CASE
        WHEN MOD(u.id, 3) = 0 THEN 'Movilidad independiente'
        WHEN MOD(u.id, 3) = 1 THEN 'Usa bastón ocasionalmente'
        ELSE 'Movilidad con apoyo'
    END,
    'Perfil médico de prueba para validación del sistema.',
    'Hábitos generales de prueba para el entorno de desarrollo.',
    20.00 + MOD(u.id, 10)
FROM usuarios u
WHERE u.correo LIKE 'adulto_prueba_%@mita.test';


-- =========================================================
-- 8. CREAR PERFIL DE CUIDADOR
-- =========================================================

INSERT INTO cuidador
(
    id_usuario,
    cedula_medica,
    especialidad,
    id_tipo_cuidador
)
SELECT
    u.id,
    CONCAT('CED-TEST-', LPAD(
        CAST(
            SUBSTRING_INDEX(
                SUBSTRING_INDEX(u.correo, '_', -1),
                '@',
                1
            ) AS UNSIGNED
        ),
        3,
        '0'
    )),
    CASE MOD(
        CAST(
            SUBSTRING_INDEX(
                SUBSTRING_INDEX(u.correo, '_', -1),
                '@',
                1
            ) AS UNSIGNED
        ),
        4
    )
        WHEN 0 THEN 'Geriatría'
        WHEN 1 THEN 'Enfermería'
        WHEN 2 THEN 'Fisioterapia'
        ELSE 'Atención geriátrica'
    END,
    MOD(
        CAST(
            SUBSTRING_INDEX(
                SUBSTRING_INDEX(u.correo, '_', -1),
                '@',
                1
            ) AS UNSIGNED
        ) - 1,
        4
    ) + 1
FROM usuarios u
WHERE u.correo LIKE 'cuidador_prueba_%@mita.test';


-- =========================================================
-- 9. CREAR PERFIL DE FAMILIAR
-- =========================================================

INSERT INTO familiar
(
    id_usuario
)
SELECT
    u.id
FROM usuarios u
WHERE u.correo LIKE 'familiar_prueba_%@mita.test';


-- =========================================================
-- 10. VINCULAR CADA ADULTO CON SU CUIDADOR
--     adulto 01 -> cuidador 01
--     adulto 02 -> cuidador 02
--     ...
--     adulto 30 -> cuidador 30
-- =========================================================

INSERT INTO adulto_cuidador
(
    id_adulto,
    id_cuidador,
    activo,
    observaciones
)
SELECT
    am.id,
    c.id,
    1,
    'Vinculación de prueba'
FROM adulto_mayor am
JOIN usuarios ua
    ON ua.id = am.id_usuario
JOIN usuarios uc
    ON uc.correo = CONCAT(
        'cuidador_prueba_',
        SUBSTRING(
            ua.correo,
            LENGTH('adulto_prueba_') + 1,
            2
        ),
        '@mita.test'
    )
JOIN cuidador c
    ON c.id_usuario = uc.id
WHERE ua.correo LIKE 'adulto_prueba_%@mita.test';


-- =========================================================
-- 11. VINCULAR CADA ADULTO CON SU FAMILIAR
-- =========================================================

INSERT INTO relaciones_familiar
(
    id_familiar,
    id_adulto,
    tipo_relacion,
    autorizado
)
SELECT
    f.id,
    am.id,
    'Hijo/a',
    1
FROM adulto_mayor am
JOIN usuarios ua
    ON ua.id = am.id_usuario
JOIN usuarios uf
    ON uf.correo = CONCAT(
        'familiar_prueba_',
        SUBSTRING(
            ua.correo,
            LENGTH('adulto_prueba_') + 1,
            2
        ),
        '@mita.test'
    )
JOIN familiar f
    ON f.id_usuario = uf.id
WHERE ua.correo LIKE 'adulto_prueba_%@mita.test';


-- =========================================================
-- 12. PREFERENCIAS INICIALES
-- =========================================================

INSERT INTO preferencias_usuario
(
    id_usuario,
    preferencias
)
SELECT
    u.id,
    JSON_OBJECT(
        'tema', 'claro',
        'idioma', 'es',
        'tamano_fuente', 'normal',
        'notificaciones', TRUE
    )
FROM usuarios u
WHERE u.correo LIKE '%@mita.test';


-- =========================================================
-- 13. CONFIRMAR QUE SE CREARON 100
-- =========================================================

COMMIT;

SELECT
    rol,
    COUNT(*) AS cantidad
FROM usuarios
WHERE correo LIKE '%@mita.test'
GROUP BY rol
ORDER BY rol;

SELECT COUNT(*) AS total_usuarios_prueba
FROM usuarios
WHERE correo LIKE '%@mita.test';

SELECT COUNT(*) AS adultos_prueba
FROM adulto_mayor am
JOIN usuarios u ON u.id = am.id_usuario
WHERE u.correo LIKE '%@mita.test';

SELECT COUNT(*) AS cuidadores_prueba
FROM cuidador c
JOIN usuarios u ON u.id = c.id_usuario
WHERE u.correo LIKE '%@mita.test';

SELECT COUNT(*) AS familiares_prueba
FROM familiar f
JOIN usuarios u ON u.id = f.id_usuario
WHERE u.correo LIKE '%@mita.test';

SELECT COUNT(*) AS vinculaciones_adulto_cuidador
FROM adulto_cuidador ac
JOIN adulto_mayor am ON am.id = ac.id_adulto
JOIN usuarios u ON u.id = am.id_usuario
WHERE u.correo LIKE '%@mita.test';

SELECT COUNT(*) AS vinculaciones_familiar
FROM relaciones_familiar rf
JOIN adulto_mayor am ON am.id = rf.id_adulto
JOIN usuarios u ON u.id = am.id_usuario
WHERE u.correo LIKE '%@mita.test';
