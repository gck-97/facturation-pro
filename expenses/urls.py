from django.urls import path
from . import views

app_name = 'expenses'

urlpatterns = [
    path('', views.expense_list, name='expense_list'),
    path('ajouter/', views.expense_create, name='expense_create'),
    path('modifier/<int:pk>/', views.expense_update, name='expense_update'),
    path('supprimer/<int:pk>/', views.expense_delete, name='expense_delete'),
]
