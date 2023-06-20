from django.db import models
from cliente.models import Cliente
from produto.models import Produto
from vendedor.models import Vendedor
from django.utils import timezone


class Contrato(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    vendedor = models.ForeignKey(Vendedor, on_delete=models.CASCADE)
    data_contrato = models.DateField(null=True, blank=True)
    data_instalacao = models.DateField(null=True, blank=True)
    total_contrato = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    flcancelado = models.BooleanField(default=False)
    class Meta:
        db_table = 'contrato'

class ItemContrato(models.Model):
    contrato = models.ForeignKey(Contrato, on_delete=models.CASCADE)
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.IntegerField(default=1)
    valor_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    data_item = models.DateTimeField(auto_now_add=True)
    flcancelado = models.BooleanField(default=False) 
    class Meta:
        db_table = 'item_contrato'

class EventoTipo(models.Model):
    nome = models.CharField(max_length=50)  
    class Meta:
        db_table = 'evento_tipo'

class ContratoEvento(models.Model):
    contrato = models.ForeignKey(Contrato, on_delete=models.CASCADE)
    evento_tipo = models.ForeignKey(EventoTipo, on_delete=models.CASCADE)
    evento_descricao = models.CharField(max_length=255)
    evento_data = models.DateTimeField(default=timezone.now) 
    valor_alterado = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    class Meta:
        db_table = 'contrato_evento'