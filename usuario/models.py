from django.db import models
from django.contrib.auth.models import User

class Usuario(models.Model):

    SEXO_CHOICES = (
        ("Masculino", "MASCULINO"),
        ("Feminino", "FEMININO"),
        ("Outro", "OUTRO GENERO")
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cpf = models.CharField(max_length=14, blank=False, unique=True)
    rg = models.CharField(max_length=30, blank=False)
    sus = models.CharField(max_length=50, blank=False, unique=True)
    logradouro = models.CharField(max_length=50, blank=False)
    numero = models.IntegerField(blank=False)
    complemento = models.CharField(max_length=50, blank=True)
    bairro = models.CharField(max_length=50, blank=False)
    cidade = models.CharField(max_length=50, blank=False)
    estado = models.CharField(max_length=2, blank=False)
    cep = models.CharField(max_length=8, blank=False)
    telefone = models.CharField(max_length=15, blank=False)
    sexo = models.CharField(max_length=20, choices=SEXO_CHOICES, blank=False, null=False)
    imagem = models.FileField(upload_to='fotos_usuarios', null=True, blank=True)
    notificacao = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.user.first_name + self.cpf

