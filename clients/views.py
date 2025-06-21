# clients/views.py

from django.shortcuts import render, redirect, get_object_or_404 # Ajoutez redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages # Pour les messages de succès
from .models import Client
from .forms import ClientForm # <-- Importer notre nouveau formulaire
from django.db.models import ProtectedError
from django.http import JsonResponse # <-- Ajoutez cet import
import json # <-- Ajoutez cet import

@login_required
def client_list(request):
    # ... (votre vue client_list existante, inchangée) ...
    clients = Client.objects.filter(user=request.user).order_by('nom')
    context = {
        'clients_list': clients,
        'page_title': 'Mes Clients'
    }
    return render(request, 'clients/client_list.html', context)

# NOUVELLE VUE pour créer un client
@login_required
def client_create(request):
    if request.method == 'POST':
        # Si le formulaire est soumis, on le traite
        form = ClientForm(request.POST)
        if form.is_valid():
            # On sauvegarde le formulaire mais sans l'enregistrer tout de suite en base de données
            client = form.save(commit=False)
            # On assigne l'utilisateur connecté comme propriétaire du client
            client.user = request.user
            # On sauvegarde maintenant l'objet client complet
            client.save()

            messages.success(request, f"Le client '{client.nom}' a été créé avec succès !")
            return redirect('clients:client_list') # Redirige vers la liste des clients
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
    else:
        # Si c'est une requête GET, on affiche simplement le formulaire vide
        form = ClientForm()

    context = {
        'form': form,
        'page_title': 'Ajouter un nouveau client'
    }
    return render(request, 'clients/client_form.html', context)

# NOUVELLE VUE pour modifier un client
@login_required
def client_update(request, client_id):
    # On récupère le client spécifique à modifier, en s'assurant qu'il appartient bien à l'utilisateur connecté
    client_to_update = get_object_or_404(Client, id=client_id, user=request.user)

    if request.method == 'POST':
        # On passe 'instance=client_to_update' pour dire à Django de modifier cet objet
        # au lieu d'en créer un nouveau.
        form = ClientForm(request.POST, instance=client_to_update)
        if form.is_valid():
            form.save()
            messages.success(request, f"Le client '{client_to_update.nom}' a été mis à jour avec succès !")
            return redirect('clients:client_list')
    else:
        # Si c'est une requête GET, on pré-remplit le formulaire avec les données du client existant
        form = ClientForm(instance=client_to_update)

    context = {
        'form': form,
        'page_title': f"Modifier le client : {client_to_update.nom}"
    }
    # On réutilise le même template que pour la création !
    return render(request, 'clients/client_form.html', context)

@login_required
def client_delete(request, client_id):
    client_to_delete = get_object_or_404(Client, id=client_id, user=request.user)

    if request.method == 'POST':
        try:
            # On essaie de supprimer le client
            client_name = client_to_delete.nom
            client_to_delete.delete()
            messages.success(request, f"Le client '{client_name}' a été supprimé avec succès.")
            return redirect('clients:client_list')
        except ProtectedError as e:
            # Si une ProtectedError est levée, on prépare un message d'erreur clair
            # et on récupère les objets qui bloquent la suppression
            messages.error(request, f"Impossible de supprimer le client '{client_to_delete.nom}' car il est lié à un ou plusieurs documents.")
            # e.protected_objects est un ensemble de tous les objets qui empêchent la suppression
            context = {
                'client': client_to_delete,
                'protected_objects': e.protected_objects
            }
            return render(request, 'clients/client_delete_error.html', context)

    # Si c'est une requête GET, on affiche la page de confirmation comme avant
    context = {
        'client': client_to_delete,
        'page_title': f"Supprimer le client : {client_to_delete.nom}"
    }
    return render(request, 'clients/client_confirm_delete.html', context)

@login_required
def client_create_ajax(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        client_name = data.get('name')

        if client_name:
            # Vérifier si un client avec le même nom n'existe pas déjà pour cet utilisateur
            if Client.objects.filter(user=request.user, nom=client_name).exists():
                return JsonResponse({'error': 'Un client avec ce nom existe déjà.'}, status=400)

            # Créer le nouveau client
            client = Client.objects.create(
                user=request.user,
                nom=client_name,
                email=data.get('email', ''),
                telephone=data.get('telephone', ''),
                adresse_ligne1=data.get('address', ''),
                code_postal=data.get('postal_code', ''),
                ville=data.get('city', ''), # <-- CORRECTION ICI : 'get' au lieu de 'gert'
                numero_tva=data.get('vat_number', '')
            )
            # Renvoyer les informations du nouveau client
            return JsonResponse({'id': client.id, 'name': client.nom})

    return JsonResponse({'error': 'Requête non valide'}, status=400)