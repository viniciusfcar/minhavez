from django.db import models
from django.contrib.auth.models import User

class Responsavel(models.Model):
    nome = models.CharField(max_length=20, blank=False)
    sobrenome = models.CharField(max_length=20, blank=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=False)

    def __str__(self):
        return self.nome
