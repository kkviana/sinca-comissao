from django.urls import path
from . import views
from dashboard.views import dashboard_contratos

urlpatterns = [
    path('home', dashboard_contratos, name='index'),
    path('', views.redirecionar_login),
    path('login/', views.usuario_login, name='login'),
]
