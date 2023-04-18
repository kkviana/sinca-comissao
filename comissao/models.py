from django.db import models
from contrato.models import Contrato

class Comissao(models.Model):
    valor_contrato_mes = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    contrato = models.ForeignKey(Contrato, null=True, on_delete=models.CASCADE)
    data = models.CharField(max_length=7)

    class Meta:
        db_table = 'comissao'
