# core/urls.py

from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.dashboard, name='dashboard'), # L'URL racine du site pointera vers le tableau de bord
    path('signup/', views.signup, name='signup'),

     path('initialiser-mon-admin-secret-789xyz/', views.create_superuser_view, name='create_superuser'),
]