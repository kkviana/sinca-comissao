from django.urls import path
from .views import dashboard_contratos, vendas_por_mes_ano, cancelamentos_por_mes_ano, vendas_por_mes_ano_valor, cancelamentos_por_mes_ano_valor, saldo_por_mes_ano_valor, saldo_por_mes_ano, dashboard_vendedores, vendas_por_mes_vendedor,vendas_por_mes_vendedor_valor

urlpatterns = [
    path('', dashboard_contratos, name='dashboard_contratos'),
    path('vendas-por-mes/<int:ano>/', vendas_por_mes_ano, name='vendas_por_mes_ano'),
    path('cancelamentos-por-mes/<int:ano>/', cancelamentos_por_mes_ano, name='cancelamentos_por_mes_ano'),
    path('valor-por-mes/<int:ano>/', vendas_por_mes_ano_valor, name='vendas_por_mes_ano_valor'),
    path('cancelamentos-por-mes-valor/<int:ano>/', cancelamentos_por_mes_ano_valor, name='cancelamentos_por_mes_ano_valor'),
    path('saldo-por-mes-valor/<int:ano>/', saldo_por_mes_ano_valor, name='saldo_por_mes_ano_valor'),
    path('saldo-por-mes/<int:ano>/', saldo_por_mes_ano, name='saldo_por_mes_ano'),
    path('vendedores/', dashboard_vendedores, name='dashboard_vendedores'),
    path('vendas_por_mes_vendedor/<int:ano>/', vendas_por_mes_vendedor, name='vendas_por_mes_vendedor'),
    path('vendas_por_mes_vendedor_valor/<int:ano>/', vendas_por_mes_vendedor_valor, name='vendas_por_mes_vendedor_valor'),
    
]
