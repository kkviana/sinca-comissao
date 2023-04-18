from django.urls import path
from vendedor import views

urlpatterns = [
    path('cadastrar_vendedor/', views.cadastrar_vendedor, name='cadastrar_vendedor'),
    path('lista_vendedores/', views.lista_vendedores, name='lista_vendedores'),
    path('inativar_vendedor/<int:id_vendedor>/', views.inativar_vendedor, name='inativar_vendedor'),
] 