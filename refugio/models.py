from django.db import models


class Especie(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.TextField('descripción')

    def __str__(self):
        return self.nombre


class Mascota(models.Model):
    nombre = models.CharField(max_length=80)
    descripcion = models.TextField('descripción')
    sexo = models.CharField(max_length=10, choices=[
        ('Hembra', 'Hembra'), ('Macho', 'Macho'),
    ])
    edad_aproximada = models.PositiveIntegerField(
        'edad aproximada (años)', help_text='Ingresa solo el número. Usa 0 si tiene menos de un año.')
    imagen = models.URLField('URL de la imagen', max_length=500)
    especie = models.ForeignKey(Especie, on_delete=models.PROTECT)
    tamano = models.CharField('tamaño', max_length=20, choices=[
        ('Pequeño', 'Pequeño'), ('Mediano', 'Mediano'), ('Grande', 'Grande'),
    ])
    estado = models.CharField(max_length=30, choices=[
        ('Disponible', 'Disponible'),
        ('En proceso de adopción', 'En proceso de adopción'),
        ('Adoptada', 'Adoptada'),
    ], default='Disponible')

    def __str__(self):
        return self.nombre
