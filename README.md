# Instalación y ejecución

Requiere Python 3.10 o superior, pip y venv. Ejecutar los comandos desde la carpeta que contiene `manage.py`.

## Instalar dependencias

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt

## Configurar la base de datos

Se utiliza SQLite. Para crear la base, cargar los datos iniciales, crear un administrador y configurar los grupos:

```bash
python manage.py migrate
python manage.py loaddata datos_iniciales
python manage.py createsuperuser
python manage.py configurar_roles
```

Estos pasos corresponden a la instalación inicial. `createsuperuser` solicita las credenciales del administrador.

## Ejecutar la aplicación

```bash
python manage.py runserver
```

Aplicación: http://127.0.0.1:8000/

Administración: http://127.0.0.1:8000/admin/
