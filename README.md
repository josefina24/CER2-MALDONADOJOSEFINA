# Huellas del Puerto — CER2

Aplicación de adopción desarrollada con Python y Django. Continúa el diseño del CER1 y agrega base de datos, catálogo dinámico, filtro por especie, detalle, autenticación y gestión con permisos.

## Requisitos

- Python 3.10 o superior (recomendado: 3.12).
- pip y venv para la versión de Python elegida.
- Internet para descargar Django y mostrar Bootstrap desde su CDN.
- SQLite viene con Python; no se instala MySQL ni PostgreSQL.

En WSL/Ubuntu revisa `python3 --version`. Ubuntu 20.04 puede tener Python 3.8: esa versión no sirve para Django 5.2. Si tienes Python 3.12 instalado, reemplaza `python3` por `python3.12` al crear el entorno. Si aparece un error de `venv`, instala el paquete `venv` correspondiente a esa versión de Python.

## Instalación en WSL/Ubuntu

Descomprime el ZIP en una carpeta nueva. Entra en la carpeta que contiene `manage.py`; no mezcles los archivos con el CER1.

```bash
cd Huellas_del_Puerto_CER2
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py loaddata datos_iniciales
python manage.py createsuperuser
python manage.py runserver
```

`createsuperuser` solicita nombre de usuario, correo opcional y contraseña dos veces. Al escribir la contraseña no se muestran caracteres. Elige tú las credenciales: el proyecto no incluye usuarios ni contraseñas precargados.

Abre **http://127.0.0.1:8000/**. Las imágenes de los datos iniciales usan esa dirección y el puerto 8000. Están incluidas en `static/imagenes/` y se referencian mediante URLs absolutas, de acuerdo con el campo `URLField` del modelo. Si cambias de servidor o de puerto, cambia también esas URLs en el administrador o en los datos iniciales antes de cargarlos.

`migrate` crea la base `db.sqlite3` y las tablas usando las migraciones entregadas. No necesitas ejecutar `makemigrations` al instalar. `loaddata` carga tres especies y nueve mascotas; úsalo al comenzar, porque repetirlo reemplaza los valores de los registros iniciales que tengan los mismos identificadores.

## Instalación en Windows sin WSL

Desde PowerShell, dentro de la carpeta del proyecto:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py loaddata datos_iniciales
.\.venv\Scripts\python.exe manage.py createsuperuser
.\.venv\Scripts\python.exe manage.py runserver
```

## Volver a abrirlo otro día

En WSL, entra a la carpeta del proyecto, activa el entorno y ejecuta:

```bash
source .venv/bin/activate
python manage.py runserver
```

No vuelvas a crear usuarios ni a cargar los datos iniciales. Los cambios quedan en `db.sqlite3`. Detén el servidor con Ctrl+C.

## Usuarios y grupos fijos

Después de migrar, ejecuta una vez:

```bash
python manage.py configurar_roles
```

Este comando crea los grupos **Administradores** y **Colaboradores** con permisos predeterminados. Adapta las cuentas existentes: los superusuarios quedan como Administradores y todos los demás como Colaboradores. Reemplaza sus grupos y elimina permisos individuales anteriores para aplicar el esquema fijo. Conserva nombres, contraseñas, datos personales y estado activo/inactivo. No borra mascotas ni especies. Puede repetirse para restablecer los grupos.

Si ejecutas `createsuperuser` después, ese usuario puede ingresar inmediatamente al administrador. Ejecuta de nuevo `configurar_roles` para que también quede asociado al grupo Administradores.

En `/admin/`, entra a Usuarios y pulsa Añadir. Completa usuario, contraseña y **Rol**. Solo hay dos opciones:

| Rol | Catálogo y detalle | Gestión | Agregar/modificar mascotas | Administración | Crear usuarios |
|---|---|---|---|---|---|
| Visitante sin sesión | Sí | No: pide login | No | No | No |
| Colaborador activo | Sí | Sí | Sí | No | No |
| Administrador activo | Sí | Sí | Sí | Sí | Sí, de ambos roles |

El administrador nuevo tiene las mismas facultades que el inicial: se implementa como superusuario y staff. El colaborador no es staff ni superusuario; su grupo tiene exclusivamente `view_mascota`, `add_mascota` y `change_mascota`. No puede eliminar mascotas, administrar especies ni crear cuentas. Los grupos no se editan desde la interfaz y no se muestran casillas de permisos individuales.

Una cuenta nueva creada por consola mediante `create_user`, sin grupo ni permisos, no puede entrar a Gestión hasta asignarle el rol desde Admin o ejecutar el comando. Un usuario sin permisos recibe 403; un visitante sin sesión se redirige al login.

No se registró un nuevo modelo de usuario ni se cambió la estructura de datos. El formulario de usuarios reutiliza las clases de Django y agrega un selector de rol. Al guardar se asigna el grupo y se actualizan automáticamente staff/superusuario.

## Cancelar formularios del administrador

En los formularios normales aparece arriba **Cancelar y volver a la lista**. Es un enlace que no envía el formulario ni exige completar campos. En la ventana emergente que abre el botón `+` aparece **Cancelar y cerrar ventana**. Es un botón de tipo `button`, cuyo JavaScript solo cierra la ventana. Ambos descartan los cambios sin guardar. La ventana emergente debe abrirse desde el botón `+`; los navegadores permiten cerrar por código las ventanas que abrió el propio sitio.

## Rutas

| Dirección | Uso |
|---|---|
| `/` | Presentación y tres mascotas destacadas |
| `/mascotas/` | Catálogo completo |
| `/mascotas/?especie=2` | Gatos de los datos iniciales |
| `/mascotas/1/` | Detalle de Lola |
| `/cuentas/ingresar/` | Inicio de sesión |
| `/cuentas/salir/` | Cierre de sesión mediante POST desde el botón |
| `/gestion/` | Lista interna para usuarios autenticados |
| `/gestion/agregar/` | Alta con permiso add_mascota |
| `/gestion/1/editar/` | Modificación con permiso change_mascota |
| `/admin/` | Administración de especies, mascotas y usuarios |
| `/adopcion/` | Formulario demostrativo heredado del CER1 |

## Verificar

```bash
python manage.py check
python manage.py test
```

Se incluyen 22 pruebas que comprueban catálogo, filtro, detalle, errores, login, logout, grupos fijos, creación de administradores y colaboradores, cambios de rol, cancelación, acceso directo GET/POST, validación, CSRF y acceso a los modelos del administrador. Se ejecutan sobre una base de pruebas separada y no cambian tus mascotas.

## Relación con CER2

| Requisito | Implementación |
|---|---|
| RF01 Principal | `inicio()` y `templates/refugio/inicio.html` |
| RF02 Catálogo dinámico | `catalogo()`, `Mascota.objects.all()` y bucle de tarjetas |
| RF03 Detalle | `detalle()`, identificador en URL y `detalle.html` |
| RF04 Especies | Modelo `Especie` y ForeignKey en `Mascota` |
| RF05 Filtro | GET `especie` y consulta `.filter()` |
| RF06 Administración | Ambos modelos registrados en el sitio de administración de `refugio/admin.py` |
| RF07 Interfaz reutilizable | `base.html`, `tarjeta.html` y `static/` |
| RF08 Inicio de sesión | `LoginView`, usuario de Django y template de login |
| RF09 Cierre de sesión | `LogoutView` y formulario POST con CSRF |
| RF10 Sección restringida | `@login_required` y permiso view_mascota en `gestion()` |
| RF11 Autorización | Grupos fijos y permisos add_mascota y change_mascota en las vistas |
| RF12 Acceso directo bloqueado | Decoradores en agregar y editar, para GET y POST |

Se implementan todos los campos del diagrama propuesto. Además se mantienen tamaño y estado del CER1. El id lo crea Django automáticamente. Se usa `PROTECT` para evitar eliminar por accidente una especie que todavía tenga mascotas; primero hay que reasignar o eliminar esas mascotas.

## Alcance

La gestión propia permite listar, agregar y modificar mascotas. La eliminación y la gestión completa de especies se realizan en Django Admin. CER2 no exige una pantalla propia para eliminar ni un sistema de solicitudes de adopción. La página de adopción conserva el formulario del CER1, señalado expresamente como demostración: no guarda ni envía solicitudes. No hay registro público de cuentas; las crea el administrador.

Es una configuración para la presentación local (`DEBUG=True`), no una configuración de despliegue de producción.

## Entrega en GitHub y Aula

El ZIP contiene el proyecto y esta documentación. **El repositorio de CER2 no está publicado desde esta entrega**. Debes crear un repositorio público nuevo con el formato exacto **CER2-APELLIDONOMBRE**, usando tus datos como los pida la docente. El nombre del CER1 no determina necesariamente el nombre correcto del CER2.

Para conservar el proyecto anterior, usa una carpeta y un repositorio nuevos. Crea en GitHub el repositorio público vacío, sin README, licencia ni gitignore iniciales. Desde la carpeta de este proyecto:

```bash
git init
git add .
git commit -m "Implementar CER2 con Django, catalogo y permisos"
git branch -M main
```

Después ejecuta, reemplazando USUARIO y APELLIDONOMBRE por los reales:

```bash
git remote add origin https://github.com/USUARIO/CER2-APELLIDONOMBRE.git
git push -u origin main
```

Si GitHub pide autenticación, utiliza tu método habitual de acceso. No se suben `.venv`, `db.sqlite3` ni contraseñas de usuarios. Las migraciones y el archivo de datos permiten reconstruir la base de datos. Conserva `static/imagenes/` en la entrega.

En Aula adjunta el enlace al repositorio público y el ZIP. Si modificas el proyecto después, genera otro ZIP con el estado final, excluyendo `.git`, `.venv`, `db.sqlite3` y `__pycache__`.

## Material para estudiar

Lee **GUIA_EXPLICACION.md**: explica los archivos, el flujo de datos, el código de las vistas, los permisos y un guion para defender el proyecto.

Documentación de apoyo: https://docs.djangoproject.com/en/5.2/topics/auth/default/

## Edad y mascotas adoptadas

`edad_aproximada` es un número entero no negativo de años completos. Se escribe `3` y se muestra “3 años aprox.”. Se acepta `0` para una mascota menor de un año. El texto no se guarda en la base.

Las mascotas con estado Adoptada se excluyen de portada, catálogo y selector de adopción, también para usuarios autenticados que visitan esas páginas públicas. Permanecen en Gestión para colaboradores y administradores, y en Django Admin para administradores. El detalle de una adoptada solo se puede consultar con permiso `view_mascota`; un visitante recibe 404 si intenta acceder directamente. Cambiarla a Disponible o En proceso de adopción hace que vuelva al catálogo.

Al actualizar desde la versión de edad textual hay que ejecutar `python manage.py migrate`. La migración 0002 convierte edades anteriores como “3 años aprox.” a `3`; si encuentra texto ambiguo se detiene en vez de asignar una edad incorrecta. No vuelvas a cargar los datos iniciales sobre tu base existente.
