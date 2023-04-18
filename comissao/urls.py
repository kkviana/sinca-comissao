from django.urls import path
from . import views

urlpatterns = [
    path('calcular_comissao/', views.calcular_comissao, name='calcular_comissao'),
    path('listar_comissao/', views.listar_comissoes, name='listar_comissoes'),
    path('fechar_comissao/', views.fechar_comissao, name='fechar_comissao'),
]
