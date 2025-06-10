# clients/urls.py

from django.urls import path
from . import views

app_name = 'clients'

urlpatterns = [
    path('', views.client_list, name='client_list'),
    path('add/', views.client_create, name='client_create'),
    path('<int:client_id>/edit/', views.client_update, name='client_update'),
    path('<int:client_id>/delete/', views.client_delete, name='client_delete'), # <-- NOUVELLE LIGNE
    path('ajax/create/', views.client_create_ajax, name='client_create_ajax'),
]