# company_settings/models.py

from django.db import models
from django.contrib.auth.models import User
from colorfield.fields import ColorField # <-- NOUVEL IMPORT

class CompanyProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='company_profile')

    company_name = models.CharField(max_length=255, verbose_name="Nom de l'entreprise")
    address_line1 = models.CharField(max_length=255, verbose_name="Ligne d'adresse 1")
    address_line2 = models.CharField(max_length=255, blank=True, null=True, verbose_name="Ligne d'adresse 2")
    postal_code = models.CharField(max_length=20, verbose_name="Code Postal")
    city = models.CharField(max_length=100, verbose_name="Ville")
    country = models.CharField(max_length=100, default="Belgique", verbose_name="Pays")

    vat_number = models.CharField(max_length=50, blank=True, null=True, verbose_name="Numéro de TVA")
    phone_number = models.CharField(max_length=30, blank=True, null=True, verbose_name="Numéro de téléphone")
    email_address = models.EmailField(blank=True, null=True, verbose_name="Adresse e-mail")

    bank_account_number = models.CharField(max_length=50, blank=True, null=True, verbose_name="Numéro de compte (IBAN)")
    bank_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Nom de la banque")
    bic_swift = models.CharField(max_length=20, blank=True, null=True, verbose_name="BIC/SWIFT")

    logo = models.ImageField(upload_to='company_logo/', blank=True, null=True, verbose_name="Logo de l'entreprise")

    # CHAMP MODIFIÉ : on utilise ColorField au lieu de CharField
    accent_color = ColorField(
        default='#007bff', 
        verbose_name="Couleur d'accentuation"
    )

    terms_and_conditions = models.TextField(blank=True, null=True, verbose_name="Termes et conditions par défaut (pour factures)")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Profil de l'Entreprise"
        verbose_name_plural = "Profils d'Entreprise"

    def __str__(self):
        return f"{self.company_name} (Utilisateur: {self.user.username})"