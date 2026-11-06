from django.contrib.auth.models import Group, Permission

ROLES = [('Administradores', 'Administrador'), ('Colaboradores', 'Colaborador')]


def configurar_grupos():
    administradores, _ = Group.objects.get_or_create(name='Administradores')
    colaboradores, _ = Group.objects.get_or_create(name='Colaboradores')
    # El administrador gestiona mascotas, especies y usuarios.
    permisos_admin = Permission.objects.filter(
        content_type__app_label='refugio')
    permisos_usuarios = Permission.objects.filter(
        content_type__app_label='auth', content_type__model='user')
    administradores.permissions.set(permisos_admin | permisos_usuarios)
    # El colaborador solo consulta, agrega y modifica mascotas.
    colaboradores.permissions.set(Permission.objects.filter(
        content_type__app_label='refugio', content_type__model='mascota',
        codename__in=['view_mascota', 'add_mascota', 'change_mascota']))


def asignar_rol(usuario, rol):
    grupo = Group.objects.get(name=rol)
    usuario.groups.set([grupo])
    usuario.user_permissions.clear()
    # Los administradores nuevos tienen las mismas facultades del inicial.
    usuario.is_staff = rol == 'Administradores'
    usuario.is_superuser = rol == 'Administradores'
    usuario.save()
