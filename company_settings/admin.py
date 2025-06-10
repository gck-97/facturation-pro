# company_settings/admin.py

from django.contrib import admin
from .models import CompanyProfile

@admin.register(CompanyProfile)
class CompanyProfileAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'email_address', 'user', 'updated_at')

    # On ajoute 'accent_color' au premier fieldset
    fieldsets = (
        ("Informations Générales", {
            'fields': ('company_name', 'logo', 'email_address', 'phone_number', 'accent_color') # <-- MODIFIÉ
        }),
        ("Adresse de l'Entreprise", {
            'fields': ('address_line1', 'address_line2', 'postal_code', 'city', 'country')
        }),
        ("Informations Fiscales et Bancaires", {
            'fields': ('vat_number', 'bank_account_number', 'bank_name', 'bic_swift')
        }),
        ("Autres", {
            'fields': ('terms_and_conditions',)
        }),
    )

    def has_add_permission(self, request):
        """ Empêche un utilisateur d'ajouter plus d'un profil. """
        # La permission d'ajouter est donnée seulement s'il n'y a pas déjà
        # un profil pour cet utilisateur spécifique.
        return not CompanyProfile.objects.filter(user=request.user).exists()

    def get_queryset(self, request):
        """
        Filtre les objets pour ne montrer que ceux de l'utilisateur connecté,
        sauf si c'est un super-utilisateur.
        """
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

    def save_model(self, request, obj, form, change):
        """
        Assigne automatiquement l'utilisateur connecté lors de la création du profil.
        """
        if not obj.pk:
            obj.user = request.user
        super().save_model(request, obj, form, change)