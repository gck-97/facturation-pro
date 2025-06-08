# company_settings/urls.py

from django.urls import path
from . import views

app_name = 'company_settings'

urlpatterns = [
    # This will be the URL for your profile settings page later
    # It will correspond to the full URL: /settings/profile/
    # path('profile/', views.profile_settings_view, name='profile_settings'), 
]
