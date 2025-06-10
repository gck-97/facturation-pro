# products/forms.py

from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        # On exclut 'user' car il sera assigné automatiquement dans la vue.
        fields = ['nom', 'description', 'prix_unitaire']

        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'prix_unitaire': forms.NumberInput(attrs={'class': 'form-control'}),
        }