# Seguridad en MITA

Este documento resume las decisiones de seguridad del proyecto y el modelo de amenazas considerado. Está pensado para revisión por el docente y para futuros colaboradores.

---

## 1. Principios generales

1. **MySQL es la única base de datos clínica.** No se usa SQLite en ningún punto del código; si MySQL no está disponible, la app lo dice y se niega a guardar datos en otro formato.
2. **MongoDB solo recibe telemetría no clínica.** No guarda identidades, contraseñas, mensajes, progreso ni reportes. Si MongoDB no está disponible, la app sigue funcionando normalmente.
3. **Nunca se usan contraseñas en texto plano.** El registro y la autenticación siempre pasan por el gestor de seguridad (`core/security.py`).
4. **La aplicación nunca se conecta a MySQL como `root`.** Usa un usuario dedicado con permisos limitados sobre la base del proyecto.

---

## 2. Hash de contraseñas (`core/security.py`)

| Parámetro | Valor |
|---|---|
| Algoritmo | PBKDF2-HMAC-SHA-256 |
| Iteraciones | 310 000 |
| Sal | 16 bytes aleatorios por contraseña |
| Comparación | `hmac.compare_digest` (resistente a timing attacks) |
| Formato almacenado | `pbkdf2_sha256$iteraciones$sal_base64$hash_base64` |

Compatibilidad: si en la base existían contraseñas hasheadas con SHA-256 simple o incluso en texto plano (versiones previas), se siguen aceptando durante el inicio de sesión y se **re-hashean automáticamente a PBKDF2** la primera vez que el usuario entra. Esto evita pedir un cambio de contraseña masivo.

---

## 3. Configuración de MySQL

### 3.1 Usuario dedicado, nunca `root`

El proyecto incluye en el README los comandos SQL para crear el usuario `mita_app` con permisos limitados:

```sql
CREATE USER IF NOT EXISTS 'mita_app'@'localhost'
    IDENTIFIED BY 'coloca_una_contrasena_fuerte';

GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, INDEX, REFERENCES
    ON SistemaGeriatrico.* TO 'mita_app'@'localhost';
```

La contraseña real se guarda en `.env`, que está excluido por `.gitignore` y nunca debe subirse al repositorio.

### 3.2 Charset y collation

Todas las tablas usan `utf8mb4` con `utf8mb4_unicode_ci`, lo que evita problemas con acentos, eñes y caracteres de lenguas indígenas como el náhuatl.

### 3.3 Llaves foráneas y `ON DELETE`

Las tablas principales definen `ON DELETE CASCADE` o `ON DELETE RESTRICT` para mantener la integridad referencial. Por ejemplo, al eliminar un adulto mayor se borran en cascada sus relaciones con alergias, hábitos, dificultades, mensajes y reportes.

---

## 4. Roles y control de acceso

| Rol | Permisos |
|---|---|
| **Adulto Mayor** | Ve y modifica su propio progreso. No ve datos de otros adultos. |
| **Familiar** | Sólo ve el progreso del adulto con el que está vinculado en `relaciones_familiar.autorizado = 1`. No ve información médica sensible (alergias, perfil clínico). |
| **Cuidador** | Ve y edita todos los pacientes. Puede crear adultos mayores, familiares y compartir reportes. |
| **Administrador** | Mantenimiento del sistema. Datos sensibles enmascarados (`GestorSeguridad.enmascarar_dato_sensible`). Accede por el panel secreto con `Ctrl+Shift+A`. |

El acceso a datos sensibles **no se deriva sólo del rol**; se valida también por la relación explícita (por ejemplo, un familiar debe estar en `relaciones_familiar` con `autorizado = 1`).

---

## 5. Datos sensibles en el panel admin

El panel de administrador lista usuarios pero **enmascara contraseñas, correos y otros datos clínicos** con `GestorSeguridad.enmascarar_dato_sensible`. Esto reduce el riesgo de fuga si el panel se muestra en una pantalla compartida o queda en una captura.

---

## 6. Auditoría

La tabla `auditoria` registra:

- `accion`: nombre corto (ej. `cambio_rol`, `eliminar_usuario`).
- `detalle`: texto libre con la descripción.
- `id_admin`: usuario que ejecutó la acción.
- `fecha_hora`: timestamp del servidor MySQL.

Cada acción del `AdministradorUsuarios` deja un registro aquí.

---

## 7. Sincronización futura entre dos bases MySQL

La arquitectura propuesta plantea `mita_local` (en cada PC) y `mita_red` (servidor de la residencia o servidor global). Para esa fase se aplicarán estas medidas adicionales:

| Medida | Razón |
|---|---|
| **API REST con TLS** | Los clientes de escritorio nunca se conectan directamente al MySQL remoto. |
| **Tokens de sesión cortos** | Limitan el daño si un token se filtra. |
| **Cola `sync_outbox` con UUID por evento** | Permite replicación idempotente: si un evento se envía dos veces, el servidor lo reconoce por UUID y no lo duplica. |
| **Versión optimista para perfiles** | Ante conflicto, se muestra una comparación al cuidador en vez de sobrescribir a ciegas. |
| **Reportes con destinatarios explícitos y revocables** | `reporte_destinatarios.permiso` ∈ {`ver`, `descargar`} y `revocado_en` permite retirar el acceso. |
| **Cifrado en disco** | Recomendado en cada PC que corra la app y en el servidor de la residencia. |

---

## 8. Modelo de amenazas (resumen)

| Amenaza | Mitigación actual |
|---|---|
| Contraseña débil del usuario | PBKDF2 con sal + 310 000 iteraciones |
| Acceso con `root` desde la app | Usuario `mita_app` con permisos limitados |
| Fuga del `.env` por git | `.gitignore` excluye `.env` |
| Fuga de datos en panel admin | Enmascaramiento de datos sensibles |
| Acceso no autorizado entre roles | Validación por relación (`relaciones_familiar`) |
| Modificación directa de la base | Llaves foráneas + roles MySQL |
| Captura de pantalla con datos | Pendiente: redacción de campos clínicos en vistas |

---

## 9. Tareas pendientes antes de producción

- [ ] Cifrar campos clínicos sensibles con claves fuera de la base.
- [ ] Implementar la API REST con TLS entre cliente y servidor.
- [ ] Definir política de retención y respaldo cifrado.
- [ ] Revisar requisitos legales aplicables (LFPDPPP en México, normativa de salud).
- [ ] Pruebas de penetración antes de manipular información clínica real.

---

> Este documento es vivo. Cualquier cambio importante en el modelo de seguridad debe reflejarse aquí y en el README.
