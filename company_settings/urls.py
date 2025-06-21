# company_settings/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # ... tes autres routes ...
    path('live-pdf-preview/', views.live_pdf_preview, name='live_pdf_preview'),
    path('profil/', views.manage_profile, name='manage_profile'),
]
