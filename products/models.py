# products/models.py

from django.db import models
from django.contrib.auth.models import User # <-- AJOUTER CET IMPORT

class Product(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products') # <-- CHAMP AJOUTÉ
    
    nom = models.CharField(max_length=200, help_text="Nom du produit ou du service") # unique=True enlevé ici
    description = models.TextField(blank=True, null=True, help_text="Description détaillée du produit ou service")
    prix_unitaire = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        help_text="Prix de vente unitaire hors TVA"
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    date_mise_a_jour = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['nom']
        unique_together = ('user', 'nom') # <-- Nom du produit unique PAR utilisateur

    def __str__(self):
        return f"{self.nom} - {self.prix_unitaire} €"