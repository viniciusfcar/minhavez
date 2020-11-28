from django import forms
from .models import UnidadeSaude
from django.contrib.auth.models import User

class FormUnidadeSaude(forms.ModelForm):
    class Meta:
        model = UnidadeSaude
        fields = ['razao_social', 'cnpj', 'telefone', 'email', 'logradouro', 'numero', 'complemento', 'bairro', 'cidade', 'estado',]

class FormUser(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password']