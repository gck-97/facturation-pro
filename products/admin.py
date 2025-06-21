# products/admin.py

from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('nom', 'prix_unitaire', 'user', 'date_mise_a_jour')
    search_fields = ('nom', 'description')
    list_filter = ('user',)
    ordering = ('user', 'nom',)

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
        Assigne automatiquement l'utilisateur connecté lors de la création d'un produit.
        """
        if not obj.pk:
            obj.user = request.user
        super().save_model(request, obj, form, change)