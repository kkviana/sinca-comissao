from django.db import models

class Cliente(models.Model):
    nome = models.CharField(max_length=100)
    email = models.EmailField()
    telefone = models.CharField(max_length=20)
    flinativo = models.BooleanField(default=False)

    class Meta:
        db_table = 'cliente'