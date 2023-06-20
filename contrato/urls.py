from django.urls import path
from contrato import views


urlpatterns = [
    path('novo/', views.novo_contrato, name='novo_contrato'),
    path('listar/', views.listar_contratos, name='listar_contratos'),
    path('editar/<int:id_contrato>/', views.editar_contrato, name='editar_contrato'),
    path('contratos/adicionar-item/<int:id_contrato>/', views.adicionar_item_contrato, name='adicionar_item_contrato'),
    path('cancelar_item/<int:id_item_contrato>/', views.cancelar_item_contrato, name='cancelar_item_contrato'),
    path('contrato/cancelar/<int:id_contrato>/', views.cancelar_contrato, name='cancelar_contrato'),
    path('contrato/excluir/<int:id_contrato>/', views.excluir_contrato, name='excluir_contrato'),
    path('editar_item/<int:id_item_contrato>/', views.editar_item_contrato, name='editar_item_contrato'),
    path('atualizar_contratos/', views.atualizar_contratos, name='atualizar_contratos'),
    path('relatorio_contratos/', views.relatorio_contratos, name='relatorio_contratos'),
    path('detalhes-aumento-contratos/', views.detalhes_aumento_contratos, name='detalhes_aumento_contratos'),
]
