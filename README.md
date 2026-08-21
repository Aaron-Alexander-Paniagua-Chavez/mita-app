# MITA — Sistema de Acompañamiento Geriátrico

Aplicación de escritorio para el apoyo a adultos mayores, familiares y cuidadores.
Desarrollada como proyecto universitario de la Universidad Tecnológica de Querétaro (UTEQ).

## Descripción

MITA es una aplicación de escritorio diseñada para proporcionar apoyo integral a adultos mayores,
sus familiares y cuidadores. El sistema combina actividades físicas y cognitivas personalizadas,
seguimiento de progreso, recordatorios y opciones de comunicación para mejorar la calidad de vida
y promover el envejecimiento saludable.

La aplicación está diseñada para funcionar en entornos con y sin conexión a Internet, adaptando
su funcionalidad según la disponibilidad de red. Soporta múltiples roles de usuario con permisos
específicos y ofrece una interfaz accesible con opciones de personalización visual y de contenido.

## Características principales

- Autenticación segura de usuarios
- Múltiples roles: Adulto Mayor, Familiar, Cuidador y Administrador
- Biblioteca de actividades físicas y cognitivas con clasificación por nivel y tipo
- Filtrado inteligente de actividades según limitaciones físicas y cognitivas del usuario
- Sistema de personalización de preferencias (tema, tamaño de texto, tipo de instrucciones, etc.)
- Registro y visualización de progreso y logros
- Tiempo de uso y tiempo dedicado a actividades
- Configuración flexible mediante variables de entorno
- Interfaz accesible con soporte para modo claro/oscuro y escalado de texto
- Integración opcional con IA (Google Gemini) para asistencia conversacional
- Funcionalidad de chat mediante MQTT (local y remoto)
- Funcionamiento offline completo para características esenciales
- Almacenamiento principal en MySQL (base `SistemaGeriatrico`)
- Almacenamiento opcional en MongoDB para telemetría no clínica
- Soporte para MQTT local y remoto
- Sesión persistente y recuperación automática
- Processo de introducción (onboarding) para nuevos usuarios

## Tecnologías

- Python 3.12+
- CustomTkinter (>=5.2.0)
- MySQL-Connector-Python (>=8.0.33)
- PyMongo (>=4.7.0)
- Pillow (>=10.0.0)
- CairoSVG (>=2.7.0)
- Google Generative AI (google-genai>=1.0.0)
- Paho MQTT (>=2.1.0)
- python-dotenv (>=1.0.0)

## Requisitos

### Requisitos obligatorios

- Sistema operativo: Windows 10/11 (probado), compatible con macOS y Linux mediante adaptación
- Python 3.12 o superior
- MySQL Server 8.0 o superior (base `SistemaGeriatrico` debe existir o ser creada manualmente)
- Conexión a red local para funcionamiento básico (opcional para funciones en línea)

### Requisitos opcionales (para funciones avanzadas)

- MongoDB (para telemetría y analíticas)
- Cuenta de Google Gemini con API key (para función de IA)
- Broker MQTT accesible (para chat remoto)
- Conexión a Internet para funciones en línea (IA, chat remoto, actualizaciones)

## Instalación

1. Clonar el repositorio:
   ```bash
   git clone https://github.com/tu-usuario/mita-app.git
   cd mita-app
   ```

2. Crear y activar un entorno virtual:
   ```bash
   python -m venv .venv
   # En Windows:
   .\.venv\Scripts\activate
   # En macOS/Linux:
   source .venv/bin/activate
   ```

3. Instalar las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

4. Configurar el archivo de entorno:
   - Copiar `.env.example` a `.env`
   - Editar `.env` con las credenciales y configuraciones apropiadas
   - **Importante**: El archivo `.env` nunca debe subirse a repositorios públicos

5. Configurar MySQL:
   - Asegurarse de que MySQL está en ejecución
   - Verificar que la base de datos `SistemaGeriatrico` existe (crearla si es necesario)
   - El usuario especificado en `.env` debe tener permisos de lectura/escritura en dicha base

6. Configurar MongoDB (opcional):
   - Si se desea usar telemetría, asegurar que MongoDB está en ejecución
   - La base `mita_analytics` será utilizada automáticamente si está disponible

7. Configurar Google Gemini (opcional):
   - Obtener una API key de Google Gemini
   - Establecer la variable `GEMINI_API_KEY` en el archivo `.env`
   - Opcionalmente ajustar `GEMINI_MODEL` si se requiere un modelo específico

8. Configurar MQTT (opcional para chat):
   - Para chat local: asegurarse de que un broker MQTT local está disponible (por ejemplo, Mosquitto)
   - Para chat remoto: proporcionar las credenciales y dirección del broker en `.env`

9. Ejecutar la aplicación:
   ```bash
   python main.py
   ```

## Configuración .env

El archivo `.env` contiene las siguientes variables (ejemplo en `.env.example`):

### Configuración de MySQL
```
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DATABASE=SistemaGeriatrico
MYSQL_USER=root
MYSQL_PASSWORD=tu_contraseña_aqui
```

### Configuración de MongoDB (opcional)
```
MONGO_URI=mongodb://localhost:27017
MONGO_DATABASE=mita_analytics
```

### Configuración de Google Gemini (opcional)
```
GEMINI_API_KEY=tu_api_key_de_google_aqui
GEMINI_MODEL=gemini-3.6-flash
```

### Configuración de MQTT (opcional)
```
MQTT_HOST=tu_broker_mqtt
MQTT_PORT=8883
MQTT_TOPIC=mita/chat
MQTT_TLS=1
MQTT_USERNAME=usuario_del_broker
MQTT_PASSWORD=contraseña_del_broker
```

Para comunicación entre redes, configure un broker propio accesible por Internet con TLS y autenticación. En una red local confiable se puede usar Mosquitto con `MQTT_TLS=0`. MITA no se conecta a brokers públicos anónimos.

### Otras opciones
```
MITA_DEMO_PASSWORD=  # Solo para cargar datos de demostración
```

**Nota**: Nunca compartan ni suban el archivo `.env` a sistemas de control de versiones.

## Modo de funcionamiento

MITA adapta su comportamiento según la disponibilidad de red y servicios:

### ONLINE (Internet disponible)
- Todas las funciones están disponibles
- IA accesible si se configuró la API key
- MQTT remoto accesible si se configuró el broker
- Sincronización de datos con servicios externos (si aplica)
- Actualizaciones y verificaciones en línea

### LOCAL (Sin Internet, pero con red local)
- Funciones principales disponibles sin conexión a Internet
- IA no disponible (requiere Internet)
- MQTT local disponible si se configuró un broker local
- Chat local disponible mediante broker en la red local
- Almacenamiento y sincronización local funcionan normalmente

### OFFLINE (Sin red)
- Todas las funciones locales disponibles
- IA desactivada
- MQTT desactivado
- Funcionamiento completamente autónomo
- Los datos se almacenan localmente y se sincronizan cuando se recupera la conexión

## Bases de datos

### MySQL

MITA utiliza una base de datos MySQL llamada `SistemaGeriatrico` para almacenar:
- Usuarios y perfiles
- Credenciales (hash de contraseñas)
- Actividades físicas y cognitivas
- Progreso y logros de usuarios
- Preferencias y personalización
- Recordatorios y configuraciones
- Datos de comunidad y publicaciones
- Información de medicamentos (si aplica)

Al iniciar, la aplicación:
1. Intenta conectarse a MySQL usando las credenciales del archivo `.env`
2. Verifica que la base de datos `SistemaGeriatrico` exista
3. Si la base no existe, muestra un error y requiere configuración manual
4. Crea las tablas necesarias si no existen (usando `CREATE TABLE IF NOT EXISTS`)
5. Nunca elimina ni modifica tablas existentes de forma destructiva
6. Preserva todos los datos existentes

### MongoDB

MongoDB es opcional y se utiliza para:
- Telemetría no clínica (tiempo de uso, tiempo de actividades)
- Métricas de anonimas para mejora del producto
- Almacenamiento de sesiones no sensibles
- Estadísticas de uso general

Si MongoDB no está disponible o no se configura:
- La aplicación continúa funcionando normalmente
- Las funciones de telemetría se desactivan silenciosamente
- No se pierde funcionalidad crítica ni se afecta la experiencia del usuario

## IA

La función de Inteligencia Artificial es opcional y se basa en:
- Google Gemini (modelo configurable mediante `GEMINI_MODEL`)
- Requiere conexión a Internet y una API key válida
- Configurable mediante la variable `GEMINI_API_KEY` en `.env`
- No transmite información clínica o sensible (diagnósticos, medicamentos, IMC, etc.)
- Mantiene contexto de conversación para interacciones coherentes
- Se desactiva gracefully si no se proporciona API key o falla la conexión
- Accesible desde el panel de administrador para pruebas y uso

## Chat

El sistema de chat utiliza MQTT para comunicación en tiempo real:
- Soporta tanto brokers locales como remotos
- Cuando hay Internet disponible y se configura un broker remoto, se usa ese
- Cuando solo hay red local, se puede usar un broker local (ej: Mosquitto en la misma red)
- Si no hay conexión MQTT disponible, el chat se desactiva gracefully
- Se requiere un broker configurado; MITA no utiliza brokers públicos anónimos
- La aplicación no envía información clínica mediante el chat
- Todos los roles autenticados pueden participar en el canal general de mensajes

## Personalización y accesibilidad

MITA ofrece extensive opciones de personalización:
- **Temas**: Claro, Oscuro y otros temas predefinidos
- **Modo claro/oscuro**: Alternar entre interfaces claras y oscuras
- **Escalado de texto**: Incrementos desde 80% hasta 200% en pasos de 10%
- **Tamaño de fuente**: Ajuste específico del tamaño de texto de la interfaz
- **Tipo de instrucciones**: Seleccionar entre ilustraciones, animaciones o texto
- **Animaciones**: Habilitar o deshabilitar efectos de transición
- **Recordatorios diarios**: Activar/desactivar notificaciones de actividades programadas
- **Idioma**: Soporte para múltiples idiomas (actualmente español e inglés)
- **Preferencias de actividades**: Seleccionar tipos de actividades preferidas
- **Limitaciones físicas**: Declarar limitaciones como rodilla, espalda, cadera, etc.
- **Limitaciones cognitivas**: Declarar dificultades como alzheimer, demencia, pérdida de memoria, etc.

El sistema utiliza estas preferencias para:
- Filtrar actividades inadecuadas según las limitaciones declaradas
- Ajustar la presentación de contenido según las necesidades visuales
- Proporcionar instrucciones en el formato preferido del usuario
- Mejorar la experiencia general mediante adaptación individual

## Actividades

MITA incluye una biblioteca de actividades divididas en dos categorías principales:

### Actividades físicas
- Ejercicios de movilidad, fuerza, equilibrio y flexibilidad
- Clasificadas por nivel de intensidad (1-3)
- Etiquetadas según grupos musculares y tipo de movimiento
- Incluyen instrucciones detalladas y precauciones de seguridad

### Actividades cognitivas
- Juegos de memoria, atención, lenguaje y razonamiento
- Clasificadas por nivel de dificultad (1-3)
- Etiquetadas según habilidades cognitivas objetivo
- Incluyen reglas claras y objetivos de aprendizaje

### Filtrado personalizado

El sistema evita recomendar actividades que puedan ser inapropiadas basándose en:
- Limitaciones físicas declaradas (ej: no recomendando sentadillas si se reporta problemas de rodilla)
- Limitaciones cognitivas declaradas (ej: evitando juegos de memoria complejos si se reporta demencia avanzada)
- Preferencias explícitas de exclusión de actividades
- Niveles de actividad adecuados al progreso y capacidades demostradas del usuario

**Importante**: MITA no sustituye la atención médica profesional. Las recomendaciones deben ser
validadas por profesionales de la salud cuando se trate de condiciones médicas específicas.

## Instrucciones multimedia

Los usuarios pueden seleccionar su preferencia para recibir instrucciones de actividades:

1. **Personas reales**: Videos dimostrativos con personas realizando las actividades
2. **Ilustraciones/animaciones**: Diagramas estáticos o animaciones simples que muestran los movimientos

Esta preferencia se almacena en la configuración del usuario y se aplica consistentemente
en todas las actividades. Si los recursos multimedia seleccionados no están disponibles,
el sistema muestra una notificación y utiliza el formato alternativo disponible.

## Roles

### Administrador
- Acceso completo a todas las funciones del sistema
- Gestión de usuarios, roles y permisos
- Configuración global del sistema
- Acceso a panel de administración completo
- Pruebas de funciones opcionales (IA, chat, etc.)

### Cuidador / Médico
- Visualización y seguimiento de múltiples pacientes
- Registro de actividades y progreso de pacientes asignados
- Configuración de recordatorios y planes de actividad personalizados
- Acceso limitado a configuración del sistema
- No puede modificar roles ni permisos de otros administradores

### Adulto Mayor (Paciente)
- Acceso a su perfil personal y actividades asignadas
- Registro propio de actividades completadas
- Visualización de su progreso y logros
- Personalización de su interfaz y preferencias
- Participación en actividades recomendadas según su perfil

### Familiar
- Vista de solo lectura del perfil de su familiar adulto mayor
- Visualización de progreso y actividades completadas
- Posibilidad de enviar mensajes de aliento y apoyo
- No puede modificar configuraciones ni registrar actividades en nombre del adulto mayor
- Acceso limitado según los permisos otorgados por el adulto mayor o cuidador

## Arquitectura

La aplicación sigue una arquitectura en capas:

```
Interfaz de Usuario (UI)
          ↓
Capa de Servicios (Business Logic)
          ↓
Capa de Repositorios (Data Access)
          ↓
Bases de Datos (MySQL/MongoDB)
```

Servicios opcionales se integran según disponibilidad:
- Servicio de IA (Google Gemini) → Requiere Internet y API key
- Servicio de Chat (MQTT) → Requiere broker accesible
- Servicio de Analítica (MongoDB) → Opcional, para telemetría
- Servicio de Conectividad → Monitorea estado de red y adapta comportamiento

Cada capa tiene responsabilidades bien definidas y las dependencias fluyen de arriba hacia abajo.
Los servicios opcionales se inicializan de forma segura y se degradan gracefully cuando no están disponibles.

## Estructura del proyecto

```
mita-app/
├── .claude/                 # Configuración de Claude Code
├── .git/                    # Metadatos de Git
├── .github/                 # Flujos de trabajo de GitHub
├── .venv/                   # Entorno virtual de Python
├── assets/                  # Recursos estáticos (logos, imágenes, etc.)
├── config/                  # Configuración centralizada
├── core/                    # Funcionalidades fondamentales (seguridad, sesión, conectividad)
├── database/                # Scripts y utilidades de base de datos
├── models/                  # Modelos de datos (ORM-like)
├── repositories/            # Capa de acceso a datos
├── services/                # Lógica de negocio y servicios externos
├── ui/                      # Componentes de interfaz de usuario
│   ├── views/               # Vistas principales por rol
│   ├── components/          # Componentes reutilizables de UI
│   └── i18n/                # Internacionalización
├── main.py                  # Punto de entrada de la aplicación
├── requirements.txt         # Dependencias de Python
├── .env.example             # Plantilla para configuración de entorno
├── README.md                # Este archivo
├── LICENSE                  # Licencia del proyecto
└── ...                      # Otros archivos de configuración y scripts
```

## Seguridad

MITA implementa múltiples medidas de seguridad para proteger los datos de los usuarios:

- **Almacenamiento de credenciales**: Las contraseñas se almacenan como hashes usando bcrypt, nunca en texto plano
- **Variables de entorno**: Credenciales sensibles (passwords, API keys) se almacenan exclusivamente en `.env`
- **Separación de responsabilidades**: Los roles limitan el acceso a funcionalidades y datos según necesidad
- **MQTT**: Se recomienda usar brokers locales o con autenticación/TLS para evitar interceptación
- **Información clínica**: La aplicación no transmite ni almacena datos clínicos sensibles mediante servicios públicos
- **MongoDB**: Se utiliza exclusivamente para datos no clínicos y telemetría anónima
- **Sesiones**: Las sesiones de usuario se gestionan de forma segura con expiración y renovación automática
- **Actualizaciones**: El mecanismo de actualización verifica la integridad de los paquetes antes de la instalación

**Nota importante**: Ningún usuario, incluyendo administradores, puede ver las contraseñas de otros usuarios en texto plano.
La funcionalidad de recuperación de contraseña utiliza resets seguros por token enviados al correo registrado.

## Cuentas de demostración

El sistema incluye un script opcional para generar datos de demostración:
- Ejecutar `python scripts/seed_demo.py` crea usuarios de prueba con diversos roles y progreso
- No elimina usuarios existentes ni sobrescribe datos reales
- Requiere que la base de datos `SistemaGeriatrico` exista y sea accesible
- Las cuentas de demostración utilizan contraseñas conocidas (documentadas en el script) y deben usarse únicamente en entornos de prueba
- El script incluye:
  * 10 usuarios administradores
  * 30 usuarios de rol cuidador/médico
  * 30 adultos mayores/pacientes
  * 30 usuarios familiares
  * Algunos usuarios contienen progreso, preferencias y logros de demostración para pruebas

## Pruebas

Se utilizan los siguientes métodos para verificar el correcto funcionamiento del proyecto:

### Pruebas automáticas
- `python -m compileall .` - Verifica que no haya errores de sintaxis en archivos Python
- Revisión de imports y inicialización de servicios clave

### Pruebas de integración
- Verificación de conexión a MySQL usando credenciales de `.env`
- Prueba de inicialización del servicio de IA (cuando API key está configurada)
- Prueba del servicio de personalización con campos de limitaciones
- Prueba del servicio de filtrado de actividades
- Prueba de inicialización de la aplicación completa

### Pruebas manuales
- Verificación de inicio de sesión para todos los roles
- Prueba de navegación entre vistas principales
- Prueba de guardado y carga de preferencias de usuario
- Prueba de filtrado de actividades basado en limitaciones
- Prueba de funciones de IAchat (cuando están configuradas)
- Verificación de funcionamiento en modo offline (simulando desconexión de red)

## Estado del proyecto

| Componente         | Estado       | Descripción                                                     |
|--------------------|--------------|-----------------------------------------------------------------|
| Autenticación      | Implementado | Sistema completo de login, roles y permisos                     |
| MySQL              | Implementado | Conexión automática, manejo seguro de credenciales              |
| MongoDB            | Opcional     | Funciona cuando está disponible, degradación graceful           |
| IA                 | Experimental | Funciona cuando API key configurada, requiere Internet          |
| Chat (MQTT)        | Parcial      | Funciona con brokers locales/remotos, mejora continua           |
| Personalización    | Implementado | Sistema completo de preferencias including limitaciones         |
| Filtrado de actividades | Implementado | Lógica completa de exclusión basada en limitaciones usuario    |
| UI/UX              | Implementado | Interfaz accesible con temas, modo claro/oscuro y escalado      |
| Actividades        | Implementado | Biblioteca de actividades físicas y cognitivas                  |
| Instrucciones multimedia | Parcial   | Soporte para texto e ilustraciones, videos pendiente de implementar |
| Configuración .env | Implementado | Carga segura y priorizada de variables de entorno               |
| Offline functionality | Implementado | Funcionamiento completo sin conexión a Internet                 |
| Onboarding         | Implementado | Proceso de introducción para nuevos usuarios                    |

## Hoja de ruta

Tareas pendientes para futuras mejoras:

1. **Mejorar instrucciones multimedia**: Implementar soporte completo para videos demostrativos
2. **Expandir biblioteca de actividades**: Añadir más actividades físicas y cognitivas con variadas dificultades
3. **Mejorar análisis de progreso**: Añadir visualizaciones avanzadas y reportes de tendencias
4. **Optimizar rendimiento**: Mejorar tiempos de carga y consumo de recursos en dispositivos modestos
5. **Expandir internacionalización**: Añadir soporte para más idiomas y regionalización
6. **Mejorar accesibilidad**: Implementar compatibilidad completa con lectores de pantalla y navegación teclado
7. **Añadir funciones de comunidad**: Mejorar foros y capacidades de interacción entre usuarios
8. **Implementar sistema de notificaciones push**: Para recordatorios y alertas importantes en escritorio
9. **Crear versión móvil**: Extender funcionalidad a plataformas móviles mediante framework multiplataforma
10. **Añadir soporte para múltiples vistas de calendario**: Para mejor planificación de actividades

## Licencia

Este proyecto se distribuye bajo la Licencia MIT - vea el archivo `LICENSE` para detalles.

## Autor

Aaron Alexander Paniagua Chávez
Universidad Tecnológica de Querétaro (UTEQ)

Para consultas sobre el proyecto, por favor refiérase al repositorio oficial.
