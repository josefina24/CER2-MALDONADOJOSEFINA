from io import StringIO
from django.contrib.auth.models import Group, Permission, User
from django.core.management import call_command
from django.test import Client, TestCase
from .models import Especie, Mascota
from .roles import asignar_rol


class RequisitosCER2Tests(TestCase):
    fixtures = ['datos_iniciales.json']

    def setUp(self):
        call_command('configurar_roles', stdout=StringIO())
        self.admin = User.objects.create_user('admin', password='ClavePrueba456!')
        self.colaborador = User.objects.create_user('colaborador', password='ClavePrueba456!')
        self.sin_rol = User.objects.create_user('sinrol', password='ClavePrueba456!')
        asignar_rol(self.admin, 'Administradores')
        asignar_rol(self.colaborador, 'Colaboradores')
        self.datos = {
            'nombre': 'Prueba', 'descripcion': 'Mascota de prueba',
            'sexo': 'Hembra', 'edad_aproximada': 2,
            'imagen': 'https://example.org/foto.jpg', 'especie': 1,
            'tamano': 'Pequeño', 'estado': 'Disponible',
        }

    def test_paginas_publicas(self):
        for ruta in ['/', '/mascotas/', '/adopcion/', '/mascotas/1/']:
            self.assertEqual(self.client.get(ruta).status_code, 200)
        respuesta = self.client.get('/mascotas/')
        self.assertEqual(len(respuesta.context['mascotas']), 9)
        self.assertContains(respuesta, 'Lola')

    def test_filtro_y_errores(self):
        respuesta = self.client.get('/mascotas/', {'especie': 2})
        self.assertEqual(len(respuesta.context['mascotas']), 4)
        self.assertTrue(all(m.especie_id == 2 for m in respuesta.context['mascotas']))
        self.assertNotContains(respuesta, 'Lola')
        for valor in ['abc', '9999']:
            self.assertEqual(self.client.get('/mascotas/', {'especie': valor}).status_code, 404)
        self.assertEqual(self.client.get('/mascotas/9999/').status_code, 404)

    def test_especie_sin_mascotas(self):
        especie = Especie.objects.create(nombre='Ave', descripcion='Aves')
        self.assertContains(self.client.get('/mascotas/', {'especie': especie.pk}),
                            'No hay mascotas para mostrar.')

    def test_anonimo_no_modifica_por_url_directa(self):
        for ruta in ['/gestion/', '/gestion/agregar/', '/gestion/1/editar/']:
            self.assertEqual(self.client.get(ruta).status_code, 302)
            self.assertEqual(self.client.post(ruta, self.datos).status_code, 302)
        self.assertEqual(Mascota.objects.count(), 9)
        self.assertEqual(Mascota.objects.get(pk=1).nombre, 'Lola')

    def test_usuario_sin_rol_no_entra_a_gestion(self):
        self.client.force_login(self.sin_rol)
        for ruta in ['/gestion/', '/gestion/agregar/', '/gestion/1/editar/']:
            self.assertEqual(self.client.get(ruta).status_code, 403)
            self.assertEqual(self.client.post(ruta, self.datos).status_code, 403)
        self.assertNotContains(self.client.get('/'), '>Gestión</a>')
        self.assertEqual(Mascota.objects.count(), 9)

    def test_colaborador_gestiona_mascotas(self):
        self.client.force_login(self.colaborador)
        self.assertContains(self.client.get('/gestion/'), 'Agregar mascota')
        self.assertRedirects(self.client.post('/gestion/agregar/', self.datos), '/gestion/')
        self.assertEqual(Mascota.objects.count(), 10)
        self.assertRedirects(self.client.post('/gestion/1/editar/', self.datos), '/gestion/')
        self.assertEqual(Mascota.objects.get(pk=1).nombre, 'Prueba')
        self.assertEqual(Mascota.objects.count(), 10)

    def test_colaborador_no_admin_ni_crea_usuarios(self):
        self.client.force_login(self.colaborador)
        self.assertNotContains(self.client.get('/'), '>Administración</a>')
        for ruta in ['/admin/', '/admin/auth/user/add/', '/admin/refugio/especie/add/']:
            self.assertEqual(self.client.get(ruta).status_code, 302)
            self.assertEqual(self.client.post(ruta, {'username': 'intruso'}).status_code, 302)
        self.assertFalse(User.objects.filter(username='intruso').exists())

    def test_staff_sin_superusuario_tampoco_entra_al_admin(self):
        self.sin_rol.is_staff = True
        self.sin_rol.save()
        self.client.force_login(self.sin_rol)
        self.assertEqual(self.client.get('/admin/').status_code, 302)

    def test_permisos_de_grupos_fijos(self):
        grupo = Group.objects.get(name='Colaboradores')
        self.assertSetEqual(set(grupo.permissions.values_list('codename', flat=True)),
                            {'view_mascota', 'add_mascota', 'change_mascota'})
        self.assertFalse(self.colaborador.is_staff)
        self.assertTrue(self.admin.is_superuser)
        self.assertTrue(self.admin.is_staff)
        self.assertTrue(self.admin.has_perm('auth.add_user'))

    def test_formularios_admin_solo_muestran_rol(self):
        self.client.force_login(self.admin)
        for ruta in ['/admin/auth/user/add/', f'/admin/auth/user/{self.colaborador.pk}/change/']:
            respuesta = self.client.get(ruta)
            self.assertEqual(respuesta.status_code, 200)
            self.assertContains(respuesta, 'name="rol"')
            for campo in ['groups', 'user_permissions', 'is_staff', 'is_superuser']:
                self.assertNotContains(respuesta, f'name="{campo}"')
        self.assertEqual(self.client.get('/admin/auth/group/').status_code, 404)

    def test_admin_crea_otro_admin_con_mismos_accesos(self):
        self.client.force_login(self.admin)
        respuesta = self.client.post('/admin/auth/user/add/', {
            'username': 'adminnuevo', 'password1': 'OtraClaveSegura987!',
            'password2': 'OtraClaveSegura987!', 'rol': 'Administradores',
        })
        self.assertEqual(respuesta.status_code, 302)
        usuario = User.objects.get(username='adminnuevo')
        self.assertTrue(usuario.check_password('OtraClaveSegura987!'))
        self.assertTrue(usuario.is_superuser)
        self.assertTrue(usuario.is_staff)
        self.assertTrue(usuario.groups.filter(name='Administradores').exists())
        self.client.force_login(usuario)
        self.assertEqual(self.client.get('/admin/auth/user/add/').status_code, 200)

    def test_admin_crea_colaborador_sin_aceptar_permisos_inyectados(self):
        self.client.force_login(self.admin)
        respuesta = self.client.post('/admin/auth/user/add/', {
            'username': 'colabonuevo', 'password1': 'OtraClaveSegura987!',
            'password2': 'OtraClaveSegura987!', 'rol': 'Colaboradores',
            'is_superuser': 'on', 'is_staff': 'on',
        })
        self.assertEqual(respuesta.status_code, 302)
        usuario = User.objects.get(username='colabonuevo')
        self.assertFalse(usuario.is_superuser)
        self.assertFalse(usuario.is_staff)
        self.assertTrue(usuario.has_perm('refugio.add_mascota'))
        self.assertFalse(usuario.has_perm('auth.add_user'))

    def test_cambio_de_rol_actualiza_flags_y_grupos(self):
        self.client.force_login(self.admin)
        respuesta = self.client.post(f'/admin/auth/user/{self.colaborador.pk}/change/', {
            'username': self.colaborador.username, 'rol': 'Administradores', 'is_active': 'on',
        })
        self.assertEqual(respuesta.status_code, 302)
        self.colaborador.refresh_from_db()
        self.assertTrue(self.colaborador.is_superuser)
        self.assertTrue(self.colaborador.groups.filter(name='Administradores').exists())
        self.assertEqual(self.colaborador.groups.count(), 1)
        respuesta = self.client.post(f'/admin/auth/user/{self.colaborador.pk}/change/', {
            'username': self.colaborador.username, 'rol': 'Colaboradores', 'is_active': 'on',
        })
        self.assertEqual(respuesta.status_code, 302)
        self.colaborador.refresh_from_db()
        self.assertFalse(self.colaborador.is_superuser)
        self.assertFalse(self.colaborador.is_staff)

    def test_configurar_roles_conserva_datos_y_es_repetible(self):
        clave = self.colaborador.password
        self.sin_rol.user_permissions.add(Permission.objects.get(
            content_type__app_label='auth', codename='add_user'))
        for _ in range(2):
            call_command('configurar_roles', stdout=StringIO())
        self.colaborador.refresh_from_db()
        self.sin_rol.refresh_from_db()
        self.assertEqual(self.colaborador.password, clave)
        self.assertEqual(Mascota.objects.count(), 9)
        self.assertTrue(self.sin_rol.groups.filter(name='Colaboradores').exists())
        self.assertEqual(self.sin_rol.user_permissions.count(), 0)
        self.assertEqual(Group.objects.filter(name__in=['Administradores', 'Colaboradores']).count(), 2)

    def test_cancelar_normal_y_popup_no_guarda(self):
        self.client.force_login(self.admin)
        for modelo in ['especie', 'mascota']:
            ruta = f'/admin/refugio/{modelo}/add/'
            respuesta = self.client.get(ruta)
            self.assertContains(respuesta, 'Cancelar y volver a administración')
            self.assertContains(respuesta, 'href="/admin/"')
            popup = self.client.get(ruta, {'_popup': 1})
            self.assertContains(popup, 'type="button" class="button cancelar-popup"')
            self.assertContains(popup, 'Cancelar y cerrar ventana')
            self.assertContains(popup, '/static/refugio/cancelar_admin.js')
        self.assertEqual(Mascota.objects.count(), 9)
        self.assertEqual(Especie.objects.count(), 3)

    def test_cancelar_en_altas_y_ediciones_de_los_tres_modelos(self):
        self.client.force_login(self.admin)
        for modelo, pk in [('refugio/especie', 1), ('refugio/mascota', 1),
                           ('auth/user', self.colaborador.pk)]:
            lista = f'/admin/{modelo}/'
            for ruta in [lista + 'add/', lista + f'{pk}/change/']:
                respuesta = self.client.get(ruta)
                if ruta.endswith('add/'):
                    self.assertContains(respuesta, 'Cancelar y volver a administración', count=2)
                    self.assertContains(respuesta, 'href="/admin/"')
                else:
                    self.assertContains(respuesta, 'Cancelar y volver a la lista', count=2)
                    self.assertContains(respuesta, f'href="{lista}"')
                popup = self.client.get(ruta, {'_popup': 1})
                self.assertContains(popup, 'Cancelar y cerrar ventana', count=2)
                self.assertContains(popup, 'type="button" class="button cancelar-popup"', count=2)
        self.assertEqual(User.objects.count(), 3)
        self.assertEqual(Especie.objects.count(), 3)
        self.assertEqual(Mascota.objects.count(), 9)

    def test_datos_invalidos_no_se_guardan(self):
        self.client.force_login(self.colaborador)
        self.datos['imagen'] = 'esto no es una URL'
        respuesta = self.client.post('/gestion/agregar/', self.datos)
        self.assertIn('imagen', respuesta.context['form'].errors)
        self.assertEqual(Mascota.objects.count(), 9)

    def test_login_logout_y_csrf(self):
        datos = {'username': 'colaborador', 'password': 'incorrecta'}
        self.assertEqual(self.client.post('/cuentas/ingresar/', datos).status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)
        datos['password'] = 'ClavePrueba456!'
        self.assertRedirects(self.client.post('/cuentas/ingresar/', datos), '/gestion/')
        self.assertEqual(self.client.get('/cuentas/salir/').status_code, 405)
        self.assertRedirects(self.client.post('/cuentas/salir/'), '/')
        self.assertNotIn('_auth_user_id', self.client.session)
        cliente = Client(enforce_csrf_checks=True)
        cliente.force_login(self.colaborador)
        self.assertEqual(cliente.post('/gestion/agregar/', self.datos).status_code, 403)

    def test_edad_numerica_y_sufijo_solo_en_la_vista(self):
        self.client.force_login(self.colaborador)
        respuesta = self.client.get('/gestion/agregar/')
        self.assertContains(respuesta, 'type="number"')
        self.assertRedirects(self.client.post('/gestion/agregar/', self.datos), '/gestion/')
        mascota = Mascota.objects.get(nombre='Prueba')
        self.assertEqual(mascota.edad_aproximada, 2)
        self.assertContains(self.client.get('/mascotas/'), '2 años aprox.')
        self.assertContains(self.client.get(f'/mascotas/{mascota.pk}/'), '2 años aprox.')

    def test_edades_invalidas_y_cero(self):
        self.client.force_login(self.colaborador)
        for valor in ['dos', '2 años aprox.', -1, '2.5']:
            self.datos['edad_aproximada'] = valor
            respuesta = self.client.post('/gestion/agregar/', self.datos)
            self.assertIn('edad_aproximada', respuesta.context['form'].errors)
        self.assertEqual(Mascota.objects.count(), 9)
        self.datos['edad_aproximada'] = 0
        self.assertRedirects(self.client.post('/gestion/agregar/', self.datos), '/gestion/')
        self.assertEqual(Mascota.objects.get(nombre='Prueba').edad_aproximada, 0)

    def test_adoptadas_ocultas_en_todas_las_paginas_publicas(self):
        mascota = Mascota.objects.get(pk=1)
        mascota.estado = 'Adoptada'
        mascota.save()
        # El catálogo público las oculta también cuando hay sesión.
        for usuario in [None, self.sin_rol, self.colaborador, self.admin]:
            if usuario is None:
                self.client.logout()
            else:
                self.client.force_login(usuario)
            for ruta in ['/', '/mascotas/', '/mascotas/?especie=1', '/adopcion/']:
                self.assertNotContains(self.client.get(ruta), 'Lola')
        self.client.logout()
        self.assertEqual(self.client.get('/mascotas/1/').status_code, 404)
        self.client.force_login(self.sin_rol)
        self.assertEqual(self.client.get('/mascotas/1/').status_code, 404)

    def test_adoptadas_visibles_y_editables_solo_en_gestion_y_admin(self):
        Mascota.objects.filter(pk=1).update(estado='Adoptada')
        for usuario in [self.colaborador, self.admin]:
            self.client.force_login(usuario)
            self.assertContains(self.client.get('/gestion/'), 'Lola')
            detalle = self.client.get('/mascotas/1/')
            self.assertContains(detalle, 'Adoptada')
            self.assertContains(detalle, 'Volver a gestión')
            self.assertNotContains(detalle, 'Información para adoptar')
            self.assertEqual(self.client.get('/gestion/1/editar/').status_code, 200)
        self.assertContains(self.client.get('/admin/refugio/mascota/'), 'Lola')
        self.assertEqual(self.client.get('/admin/refugio/mascota/1/change/').status_code, 200)
        # Si cambia su estado, vuelve a aparecer automáticamente en el catálogo.
        Mascota.objects.filter(pk=1).update(estado='Disponible')
        self.client.logout()
        self.assertContains(self.client.get('/mascotas/'), 'Lola')
