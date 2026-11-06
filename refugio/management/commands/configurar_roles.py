from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction
from refugio.roles import asignar_rol, configurar_grupos


class Command(BaseCommand):
    help = 'Crea los dos grupos fijos y adapta los usuarios existentes.'

    @transaction.atomic
    def handle(self, *args, **options):
        configurar_grupos()
        for usuario in User.objects.all():
            if usuario.is_superuser:
                asignar_rol(usuario, 'Administradores')
            else:
                asignar_rol(usuario, 'Colaboradores')
        self.stdout.write(self.style.SUCCESS(
            'Roles configurados: superusuarios como Administradores y '
            'otros usuarios como Colaboradores. No se cambiaron contraseñas.'))
