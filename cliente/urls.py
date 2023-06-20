from django.urls import path
from cliente import views

urlpatterns = [
    path('cadastrar_cliente/', views.cadastrar_cliente, name='cadastrar_cliente'),
    path('lista_clientes/', views.lista_clientes, name='lista_clientes'),
    path('clientes/editar/<int:id_cliente>/', views.editar_cliente, name='editar_cliente'),
    path('clientes/inativar_cliente/<int:id_cliente>/', views.inativar_cliente, name='inativar_cliente'),
    path('importar/', views.importar, name='importar'),
] 