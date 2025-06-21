# company_settings/forms.py

from django import forms
from .models import CompanyProfile
from colorfield.widgets import ColorWidget

class CompanyProfileForm(forms.ModelForm):
    class Meta:
        model = CompanyProfile
        fields = [
            'company_name', 'address_line1', 'address_line2',
            'postal_code', 'city', 'country',
            'vat_number', 'phone_number', 'email_address',
            'bank_account_number', 'bank_name', 'bic_swift',
            'logo', 'accent_color', 'terms_and_conditions'
        ]
        widgets = {
            'accent_color': ColorWidget(),  # <--- Bien (instance)
            'terms_and_conditions': forms.Textarea(attrs={'rows': 4}),
        }