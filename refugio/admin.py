from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .admin_forms import UsuarioCambioForm, UsuarioCreacionForm
from .models import Especie, Mascota
from .roles import asignar_rol, configurar_grupos


class RefugioAdminSite(admin.AdminSite):
    site_header = 'Administración de Huellas del Puerto'
    site_title = 'Huellas del Puerto'

    def has_permission(self, request):
        # Ni siquiera un usuario staff sin rol de administrador puede entrar.
        return request.user.is_active and request.user.is_superuser


class UsuarioAdmin(UserAdmin):
    add_form = UsuarioCreacionForm
    form = UsuarioCambioForm
    add_fieldsets = (
        (None, {'fields': ('username', 'password1', 'password2', 'rol')}),
    )
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Datos personales', {'fields': ('first_name', 'last_name', 'email')}),
        ('Acceso', {'fields': ('rol', 'is_active')}),
    )
    list_display = ('username', 'email', 'is_superuser', 'is_active')
    list_filter = ('is_superuser', 'is_active')
    filter_horizontal = ()

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        configurar_grupos()
        asignar_rol(form.instance, form.cleaned_data['rol'])


sitio_admin = RefugioAdminSite(name='admin')
sitio_admin.register(Especie)
sitio_admin.register(Mascota)
sitio_admin.register(User, UsuarioAdmin)
# No se registra Group: los grupos y sus permisos son fijos.
