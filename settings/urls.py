# settings/urls.py
from django.urls import path
from . import views

app_name = 'settings'

urlpatterns = [
    path('profil/', views.company_profile_view, name='company_profile'),  # URL pour afficher le profil
]
