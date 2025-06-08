# clients/models.py

from django.db import models
from django.contrib.auth.models import User # <-- AJOUTER CET IMPORT

class Client(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='clients') # <-- CHAMP AJOUTÉ
    
    nom = models.CharField(max_length=200, help_text="Nom complet ou raison sociale du client") # unique=True enlevé ici
    email = models.EmailField(max_length=254, blank=True, null=True, help_text="Adresse email du client")
    telephone = models.CharField(max_length=20, blank=True, null=True, help_text="Numéro de téléphone du client")
    adresse_ligne1 = models.CharField(max_length=255, help_text="Rue et numéro")
    adresse_ligne2 = models.CharField(max_length=255, blank=True, null=True, help_text="Ligne d'adresse supplémentaire (appartement, etc.)")
    code_postal = models.CharField(max_length=10)
    ville = models.CharField(max_length=100)
    pays = models.CharField(max_length=100, default="Belgique")
    numero_tva = models.CharField(max_length=50, blank=True, null=True, help_text="Numéro de TVA (si applicable)")
    date_creation = models.DateTimeField(auto_now_add=True)
    date_mise_a_jour = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['nom']
        unique_together = ('user', 'nom') # <-- Nom du client unique PAR utilisateur

    def __str__(self):
        return self.nom