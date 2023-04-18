from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.index, name='index'),
    path('', views.redirecionar_login),
    path('login/', views.usuario_login, name='login'),
]
