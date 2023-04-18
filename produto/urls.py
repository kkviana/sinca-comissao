from django.urls import path
from produto import views

urlpatterns = [
    path('cadastrar_produto/', views.cadastrar_produto, name='cadastrar_produto'),
    path('lista_produtos/', views.lista_produtos, name='lista_produtos'),
    path('produtos/editar/<int:id_produto>/', views.editar_produto, name='editar_produto'),
    path('produtos/inativar_produto/<int:id_produto>/', views.inativar_produto, name='inativar_produto'),
] 