from django.db import models

class Produto(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField()
    preco = models.DecimalField(max_digits=7, decimal_places=2)
    flinativo = models.BooleanField(default=False)

    class Meta:
        db_table = 'produto'