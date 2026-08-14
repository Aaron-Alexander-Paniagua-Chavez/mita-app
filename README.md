# MITA

Aplicación de escritorio para acompañar a personas adultas mayores, familiares y cuidadores.

## Datos locales

MITA utiliza una sola base MySQL local llamada `mita_local` para los usuarios, perfiles, actividades, progreso, medicamentos y comunidad. MongoDB usa la base `mita_analytics` para telemetría.

Al iniciar, la aplicación crea las bases, tablas, colecciones y datos iniciales que falten. Si MySQL solicita contraseña, la propia aplicación muestra **Configurar MySQL** y guarda la conexión sólo en esa computadora.

## Consultar MySQL

```powershell
mysql -u root -p
```

```sql
USE mita_local;
SHOW TABLES;
SELECT id, nombre, correo, rol FROM usuarios;
```

## Ejecutar

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```
