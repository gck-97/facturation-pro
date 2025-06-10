# clients/forms.py

from django import forms
from .models import Client

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        # On liste les champs du modèle Client que l'on veut dans le formulaire.
        # On exclut 'user' car il sera assigné automatiquement dans la vue.
        fields = [
            'nom', 'email', 'telephone', 
            'adresse_ligne1', 'adresse_ligne2', 
            'code_postal', 'ville', 'pays', 'numero_tva'
        ]

        # Optionnel : ajouter des widgets pour styliser avec Bootstrap
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'adresse_ligne1': forms.TextInput(attrs={'class': 'form-control'}),
            'adresse_ligne2': forms.TextInput(attrs={'class': 'form-control'}),
            'code_postal': forms.TextInput(attrs={'class': 'form-control'}),
            'ville': forms.TextInput(attrs={'class': 'form-control'}),
            'pays': forms.TextInput(attrs={'class': 'form-control'}),
            'numero_tva': forms.TextInput(attrs={'class': 'form-control'}),
        }