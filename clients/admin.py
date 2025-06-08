# clients/admin.py

from django.contrib import admin
from .models import Client

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('nom', 'email', 'ville', 'telephone', 'user') # Ajout de 'user' pour voir le propriétaire
    search_fields = ('nom', 'email', 'ville')
    list_filter = ('ville', 'pays', 'user') # Ajout de 'user' pour filtrer par utilisateur (utile pour l'admin)
    ordering = ('user', 'nom',)

    def get_queryset(self, request):
        """
        Filtre les objets pour ne montrer que ceux de l'utilisateur connecté,
        sauf si c'est un super-utilisateur.
        """
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs # Le super-utilisateur voit tout
        return qs.filter(user=request.user)

    def save_model(self, request, obj, form, change):
        """
        Assigne automatiquement l'utilisateur connecté lors de la création d'un client.
        """
        if not obj.pk: # Si l'objet n'a pas encore été créé
            obj.user = request.user # Assigne l'utilisateur actuel
        super().save_model(request, obj, form, change)