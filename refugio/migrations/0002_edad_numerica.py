import re
from django.db import migrations, models


def convertir_edades(apps, schema_editor):
    Mascota = apps.get_model('refugio', 'Mascota')
    mascotas = list(Mascota.objects.using(schema_editor.connection.alias).all())
    # Primero se revisan todas las edades para no convertir textos ambiguos.
    for mascota in mascotas:
        edad = str(mascota.edad_aproximada)
        resultado = re.fullmatch(
            r'\s*(\d+)\s*(?:años?)?\s*(?:aprox\.?|aproximadamente)?\s*',
            edad, flags=re.IGNORECASE)
        if resultado is None:
            raise ValueError(
                f'La edad de {mascota.nombre} (id {mascota.pk}) es "{edad}". '
                'Corrígela a un número de años antes de migrar.')
        mascota.edad_aproximada = int(resultado.group(1))
    for mascota in mascotas:
        mascota.save(using=schema_editor.connection.alias, update_fields=['edad_aproximada'])


class Migration(migrations.Migration):
    dependencies = [('refugio', '0001_initial')]

    operations = [
        migrations.RunPython(convertir_edades, reverse_code=migrations.RunPython.noop),
        migrations.AlterField(
            model_name='mascota',
            name='edad_aproximada',
            field=models.PositiveIntegerField(
                'edad aproximada (años)',
                help_text='Ingresa solo el número. Usa 0 si tiene menos de un año.'),
        ),
    ]
