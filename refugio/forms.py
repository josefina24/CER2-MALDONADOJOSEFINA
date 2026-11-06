from django.forms import ModelForm
from .models import Mascota


class MascotaForm(ModelForm):
    class Meta:
        model = Mascota
        fields = ['nombre', 'descripcion', 'sexo', 'edad_aproximada',
                  'imagen', 'especie', 'tamano', 'estado']
