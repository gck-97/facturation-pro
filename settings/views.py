# settings/views.py
from django.shortcuts import render
from .models import CompanyProfile

def company_profile_view(request):
    company = CompanyProfile.objects.first()  # Récupère la première entreprise (tu peux personnaliser si tu veux gérer plusieurs)
    return render(request, 'settings/company_profile.html', {'company': company})
