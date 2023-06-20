from django.contrib import admin
from django.urls import path, include
from meuapp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('produto/', include('produto.urls')),
    path('cliente/', include('cliente.urls')),
    path('contrato/', include('contrato.urls')),
    path('comissao/', include('comissao.urls')),
    path('vendedor/', include('vendedor.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('base/', views.base, name='base'),
    path('', include('core.urls')),
] 