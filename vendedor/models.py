from django.db import models

class Vendedor(models.Model):
    nome = models.CharField(max_length=100)
    flinativo = models.BooleanField(default=False)

    class Meta:
        db_table = 'vendedor'
