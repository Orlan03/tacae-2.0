# forms.py
from django import forms
from django.contrib.auth.models import User
from .models import Empleado

class EmpleadoForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Contraseña")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirmar Contraseña")
    username = forms.CharField(max_length=150, label="Nombre de usuario")

    class Meta:
        model = Empleado
        fields = ['nombres', 'apellidos', 'cedula', 'celular']  # Aquí no incluimos 'first_name' ni 'last_name'

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        
        return cleaned_data
