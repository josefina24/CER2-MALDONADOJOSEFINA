from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from .roles import ROLES


class UsuarioCreacionForm(UserCreationForm):
    rol = forms.ChoiceField(label='Rol', choices=ROLES, initial='Colaboradores')


class UsuarioCambioForm(UserChangeForm):
    rol = forms.ChoiceField(label='Rol', choices=ROLES)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.is_superuser:
            self.fields['rol'].initial = 'Administradores'
        else:
            self.fields['rol'].initial = 'Colaboradores'
