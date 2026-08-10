# MITA — Sistema de Acompañamiento Geriátrico

[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1?logo=mysql&logoColor=white)](https://www.mysql.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-7.0-47A248?logo=mongodb&logoColor=white)](https://www.mongodb.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-En%20desarrollo-orange)]()

Aplicación de escritorio para acompañar el bienestar de personas adultas mayores, sus familiares y cuidadores. Proyecto escolar de la **Universidad Tecnológica de Querétaro (UTEQ)**.

---

## 📋 Tabla de contenidos

1. [Descripción del proyecto](#-descripción-del-proyecto)
2. [Características principales](#-características-principales)
3. [Tecnologías utilizadas](#-tecnologías-utilizadas)
4. [Requisitos previos](#-requisitos-previos)
5. [Instalación](#-instalación)
6. [Configuración](#-configuración)
7. [Ejecución](#-ejecución)
8. [Arquitectura](#-arquitectura)
9. [Seguridad](#-seguridad)
10. [Estructura del proyecto](#-estructura-del-proyecto)
11. [Cuentas de demostración](#-cuentas-de-demostración)
12. [Hoja de ruta](#-hoja-de-ruta)
13. [Contribuciones](#-contribuciones)
14. [Autor](#-autor)
15. [Licencia](#-licencia)

---

## 🩺 Descripción del proyecto

MITA es una aplicación de escritorio pensada para residencias, clínicas y hogares donde se acompaña a personas adultas mayores. Permite:

- Registrar adultos mayores con su perfil médico (alergias, IMC, limitaciones de movilidad, dificultades cognitivas).
- Crear cuentas para familiares y personal de salud (cuidadores, médicos, enfermeros).
- Llevar un **progreso individual** con puntos, racha de días y logros desbloqueados.
- Realizar **ejercicios físicos y cognitivos** adaptados al nivel de movilidad.
- Compartir información entre los roles (adulto, familiar, médico) mediante **reportes de progreso** y un sistema de **mensajería** entre participantes autorizados.
- Funcionar **sin Internet** en redes locales (geriátrico) y sincronizar entre varias computadoras o hacia un servidor global cuando hay red.

El proyecto nace como trabajo escolar con el objetivo de mostrar una arquitectura profesional: **Python + MySQL + MongoDB**, patrones de diseño (Singleton, Factory, Repository), accesibilidad (tamaños de texto, modo oscuro, multilenguaje) y un modelo de seguridad pensado para datos clínicos.

---

## ✨ Características principales

- **MySQL obligatorio** para toda la información funcional (usuarios, progreso, comunidad, mensajes, reportes). SQLite no se usa en ningún punto.
- **MongoDB opcional** reservado para telemetría no clínica (métricas de uso, sesiones anónimas).
- **Barra de accesibilidad global** disponible antes y después del inicio de sesión: `A−`, `A+`, modo oscuro con switch y selector de idioma.
- **Tres idiomas**: Español, Inglés y **Náhuatl** (la lengua indígena con mayor número de hablantes en México; marcada como piloto y pendiente de validación por hablantes nativos).
- **Roles diferenciados**: Adulto Mayor, Familiar, Cuidador (médico/enfermero) y Administrador (panel secreto con `Ctrl+Shift+A`).
- **Esquema relacional completo** con tablas para conversaciones, mensajes, destinatarios, reportes de progreso, permisos de compartición y auditoría.
- **Hash de contraseñas con PBKDF2 + SHA-256** (310 000 iteraciones, sal única); nunca se guarda texto plano.

---

## 🧰 Tecnologías utilizadas

| Capa | Tecnología |
|---|---|
| Lenguaje | Python 3.11+ |
| Interfaz gráfica | [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) sobre Tkinter |
| Base de datos relacional | **MySQL 8** (`mysql-connector-python`) |
| Base de datos NoSQL (telemetría) | **MongoDB 7** (`pymongo`) |
| Imágenes | Pillow + cairosvg (logo vectorial) |
| Configuración | `python-dotenv` (variables de entorno desde `.env`) |

---

## ✅ Requisitos previos

1. **Python 3.11 o superior** — [python.org/downloads](https://www.python.org/downloads/)
2. **MySQL 8** corriendo en `localhost:3306` (o la IP/puerto que configures)
3. **MongoDB 7** (opcional, sólo para telemetría)
4. Windows 10/11, macOS o Linux con permisos para crear entornos virtuales

> Si trabajas en Windows y vas a renderizar el logo SVG, necesitas las librerías nativas de Cairo. La app tiene un fallback tipográfico si Cairo no está disponible.

---

## 🛠 Instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/Aaron-Alexander-Paniagua-Chavez/mita-app.git
cd mita-app

# 2. Crear y activar el entorno virtual
#    Windows (PowerShell)
py -m venv .venv
.\.venv\Scripts\Activate.ps1

#    macOS / Linux
python3 -m venv .venv
source .venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt
```

---

## ⚙️ Configuración

1. Copia el archivo de ejemplo y edítalo con tus credenciales:

   ```bash
   cp .env.example .env       # macOS / Linux
   copy .env.example .env     # Windows
   ```

2. Edita `.env` con tus valores. **No subas este archivo al repositorio** (ya está en `.gitignore`):

   ```env
   MYSQL_HOST=localhost
   MYSQL_PORT=3306
   MYSQL_DATABASE=SistemaGeriatrico
   MYSQL_USER=mita_app
   MYSQL_PASSWORD=coloca_una_contrasena_fuerte

   MONGO_URI=mongodb://localhost:27017
   MONGO_DATABASE=mita_analytics
   ```

3. Una sola vez, desde MySQL como administrador, crea la base y un usuario dedicado (no uses `root` desde la app):

   ```sql
   CREATE DATABASE IF NOT EXISTS SistemaGeriatrico
       CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

   CREATE USER IF NOT EXISTS 'mita_app'@'localhost'
       IDENTIFIED BY 'coloca_una_contrasena_fuerte';

   GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, INDEX, REFERENCES
       ON SistemaGeriatrico.* TO 'mita_app'@'localhost';

   FLUSH PRIVILEGES;
   ```

---

## ▶ Ejecución

```bash
python main.py
```

En el primer inicio MITA crea `SistemaGeriatrico`, todas sus tablas, catálogos y cuentas de demostración. Si MySQL no está disponible, la aplicación avisa y **no guarda datos en SQLite** ni en ningún otro motor.

---

## 🏗 Arquitectura

El proyecto sigue una arquitectura por capas:

```
┌─────────────────────────────────────────────┐
│                  UI (CustomTkinter)         │
│   ui/app.py · ui/views/role_views.py · ...  │
├─────────────────────────────────────────────┤
│              Servicios / Casos de uso       │
│  auth_service · comunidad_service · admin   │
├─────────────────────────────────────────────┤
│              Repositorios (Repository)      │
│  usuario_repository · progreso_repository   │
├─────────────────────────────────────────────┤
│        Core / Database / Seguridad          │
│   core/database.py · core/security.py       │
├─────────────────────────────────────────────┤
│         Modelos de dominio (POO)            │
│   models/usuario.py · models/progreso.py    │
├─────────────────────────────────────────────┤
│     MySQL (obligatorio) + MongoDB (opcional)│
└─────────────────────────────────────────────┘
```

### Dos bases MySQL para uso offline y online

La arquitectura propuesta (documentada en [`docs/ARQUITECTURA_SINCRONIZACION.md`](docs/ARQUITECTURA_SINCRONIZACION.md)) plantea **dos bases MySQL con el mismo esquema**:

- `mita_local`: corre en cada PC y permite seguir usando la app sin Internet ni red.
- `mita_red`: corre en una PC servidor de la residencia (LAN) o en un servidor global (Internet) y consolida los datos compartidos.

La sincronización se haría mediante una **API con TLS** y una **cola MySQL** (`sync_outbox`/`sync_inbox`) con UUIDs por evento, replicación idempotente y resolución de conflictos optimista.

> Hoy la app ya es **MySQL-only** y crea las tablas de conversaciones, mensajes y reportes; el agente de sincronización y la pantalla de mensajes privados forman parte de la siguiente fase.

---

## 🔐 Seguridad

| Medida | Detalle |
|---|---|
| Hash de contraseñas | PBKDF2-HMAC-SHA-256, 310 000 iteraciones, sal aleatoria de 16 bytes |
| Usuario MySQL dedicado | La app nunca se conecta como `root`; usa un usuario con permisos limitados |
| Roles y permisos | El acceso a datos sensibles se valida por rol y por relación explícita (familiar autorizado, cuidador, etc.) |
| Datos sensibles | En el panel admin se enmascaran correos, contraseñas y otra información clínica |
| Auditoría | Tabla `auditoria` registra las acciones administrativas |
| Sincronización futura | Se hará por API TLS con tokens de corta duración — nunca exponer MySQL a Internet directamente |

Más detalle en [`docs/SEGURIDAD.md`](docs/SEGURIDAD.md).

---

## 📂 Estructura del proyecto

```
mita-app/
├── main.py                       # Punto de entrada
├── README.md                     # Este archivo
├── LICENSE                       # Licencia MIT
├── requirements.txt              # Dependencias Python
├── .env.example                  # Plantilla de configuración (sin secretos)
├── .gitignore
│
├── assets/                       # Logo vectorial e imágenes
├── config/
│   └── settings.py               # Paleta, tipografías, conexión MySQL/Mongo
├── core/
│   ├── database.py               # Inicialización de MySQL/Mongo
│   ├── security.py               # Hash PBKDF2
│   ├── session.py                # Sesión del usuario (Singleton)
│   ├── sync.py                   # Punto de extensión para sincronización
│   └── messages.py               # Mensajes de la UI
├── database/
│   ├── mysql_schema.py           # DDL versionado (fuente de verdad)
│   └── schema.sql                # Referencia humana (no se ejecuta)
├── models/                       # Entidades de dominio (POO)
├── repositories/                 # Acceso a datos (Repository pattern)
├── services/                     # Casos de uso
├── ui/
│   ├── app.py                    # Ventana principal y barra de accesibilidad
│   ├── components.py             # Componentes accesibles reutilizables
│   ├── i18n.py                   # Español / Inglés / Náhuatl
│   └── views/                    # Vistas por rol
└── docs/
    ├── ARQUITECTURA_SINCRONIZACION.md
    └── SEGURIDAD.md
```

---

## 👥 Cuentas de demostración

La primera vez que se inicia la app se crean estas cuentas (cámbialas o elimínalas antes de usar información real):

| Rol | Correo | Contraseña |
|---|---|---|
| Administrador | `admin@mita.local` | `admin2026` |
| Adulto Mayor | `maria@mita.local` | `mita2026` |
| Familiar | `familiar@mita.local` | `mita2026` |
| Cuidador | `cuidador@mita.local` | `mita2026` |

---

## 🛣 Hoja de ruta

- [ ] Arreglar barra de accesibilidad global (modo oscuro se aplica a toda la UI)
- [ ] Pantalla de mensajería entre usuarios (tablas ya existen)
- [ ] Compartir reportes de progreso con destinatarios y permisos revocables
- [ ] Agente de sincronización local ↔ servidor con cola MySQL
- [ ] Empaquetado como `.exe` (Windows) y `.deb` (Linux) — fase final

---

## 🤝 Contribuciones

Este es un proyecto escolar abierto a la colaboración. Para participar:

1. Haz un fork del repositorio.
2. Crea una rama con tu cambio: `git checkout -b feature/mi-mejora`
3. Haz commits descriptivos.
4. Abre un Pull Request explicando qué hace tu cambio.

Si encuentras un error, usa las [plantillas de Issues](../../issues/new/choose).

---

## ✍ Autor

**Aaron Alexander Paniagua Chávez**
Universidad Tecnológica de Querétaro (UTEQ)
📧 2025310418@uteq.edu.mx
🔗 [github.com/Aaron-Alexander-Paniagua-Chavez](https://github.com/Aaron-Alexander-Paniagua-Chavez)

---

## 📄 Licencia

Este proyecto está bajo la [Licencia MIT](LICENSE). Puedes usarlo, copiarlo y modificarlo libremente citando al autor.
