

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages # <-- LIGNE AJOUTÉE/VÉRIFIÉE
from .models import Product
from .forms import ProductForm
from django.db.models import ProtectedError
from django.http import JsonResponse # <-- Ajoutez cet import
import json



@login_required
def product_list(request):
    # On récupère uniquement les produits appartenant à l'utilisateur connecté
    products = Product.objects.filter(user=request.user).order_by('nom')

    context = {
        'products_list': products,
        'page_title': 'Mes Produits et Services'
    }
    return render(request, 'products/product_list.html', context)

# NOUVELLE VUE pour créer un produit
@login_required
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.user = request.user
            product.save()
            messages.success(request, f"Le produit '{product.nom}' a été créé avec succès !")
            return redirect('products:product_list')
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
    else:
        form = ProductForm()

    context = {
        'form': form,
        'page_title': 'Ajouter un nouveau produit/service'
    }
    # On va créer un template générique 'product_form.html'
    return render(request, 'products/product_form.html', context)

@login_required
def product_update(request, product_id):
    # On récupère le produit à modifier, en s'assurant qu'il appartient bien à l'utilisateur
    product_to_update = get_object_or_404(Product, id=product_id, user=request.user)

    if request.method == 'POST':
        # On passe 'instance=product_to_update' pour modifier cet objet
        form = ProductForm(request.POST, instance=product_to_update)
        if form.is_valid():
            form.save()
            messages.success(request, f"Le produit '{product_to_update.nom}' a été mis à jour avec succès !")
            return redirect('products:product_list')
    else:
        # On pré-remplit le formulaire avec les données du produit existant
        form = ProductForm(instance=product_to_update)

    context = {
        'form': form,
        'page_title': f"Modifier le produit : {product_to_update.nom}"
    }
    # On réutilise le même template que pour la création !
    return render(request, 'products/product_form.html', context)

@login_required
def product_delete(request, product_id):
    # On récupère le produit à supprimer, en s'assurant qu'il appartient bien à l'utilisateur
    product_to_delete = get_object_or_404(Product, id=product_id, user=request.user)

    if request.method == 'POST':
        # Si le formulaire de confirmation est soumis
        try:
            product_name = product_to_delete.nom
            product_to_delete.delete()
            messages.success(request, f"Le produit '{product_name}' a été supprimé avec succès.")
            return redirect('products:product_list')
        except ProtectedError:
            # Si le produit est protégé (utilisé dans un document)
            messages.error(request, f"Impossible de supprimer le produit '{product_to_delete.nom}' car il est utilisé dans un ou plusieurs documents.")
            return redirect('products:product_list') # On redirige simplement vers la liste avec un message

    # Si c'est une requête GET, on affiche la page de confirmation
    context = {
        'product': product_to_delete,
        'page_title': f"Supprimer le produit : {product_to_delete.nom}"
    }
    return render(request, 'products/product_confirm_delete.html', context)

@login_required
def product_create_ajax(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        product_name = data.get('name')

        if product_name:
            # Vérifier si un produit avec le même nom n'existe pas déjà pour cet utilisateur
            if Product.objects.filter(user=request.user, nom=product_name).exists():
                return JsonResponse({'error': 'Un produit avec ce nom existe déjà.'}, status=400)

            # Créer le nouveau produit
            product = Product.objects.create(
                user=request.user,
                nom=product_name,
                description=data.get('description', ''),
                prix_unitaire=data.get('price', 0)
            )
            # Renvoyer les informations du nouveau produit
            return JsonResponse({'id': product.id, 'name': product.nom})

    return JsonResponse({'error': 'Requête non valide'}, status=400)