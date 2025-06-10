# core/views.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib import messages
from company_settings.models import CompanyProfile
from documents.models import Invoice, Quote
from django.db.models import Sum
from datetime import date
from django.contrib.auth import logout
from django.shortcuts import redirect

from django.http import HttpResponse
from django.contrib.auth.models import User

@login_required
def dashboard(request):
    """
    Affiche le tableau de bord avec les statistiques clés pour l'utilisateur connecté.
    """
    # 1. Factures en retard
    overdue_invoices_count = Invoice.objects.filter(
        user=request.user, 
        due_date__lt=date.today()
    ).exclude(
        status__in=[Invoice.InvoiceStatus.PAID, Invoice.InvoiceStatus.CANCELLED]
    ).count()

    # 2. Montant total des factures impayées
    unpaid_invoices = Invoice.objects.filter(
        user=request.user
    ).exclude(
        status__in=[Invoice.InvoiceStatus.PAID, Invoice.InvoiceStatus.CANCELLED]
    )
    total_unpaid_amount = unpaid_invoices.aggregate(Sum('total_amount_ttc'))['total_amount_ttc__sum'] or 0

    # 3. Devis en attente
    pending_quotes_count = Quote.objects.filter(
        user=request.user,
        status__in=[Quote.QuoteStatus.SENT, Quote.QuoteStatus.DRAFT]
    ).count()

    context = {
        'page_title': 'Tableau de Bord',
        'overdue_invoices_count': overdue_invoices_count,
        'total_unpaid_amount': total_unpaid_amount,
        'pending_quotes_count': pending_quotes_count,
    }
    return render(request, 'core/dashboard.html', context)


def signup(request):
    """
    Gère l'inscription d'un nouvel utilisateur.
    """
    if request.user.is_authenticated:
        return redirect('core:dashboard')

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Crée automatiquement un profil d'entreprise pour ce nouvel utilisateur
            CompanyProfile.objects.create(
                user=user,
                company_name=f"L'entreprise de {user.username}"
            )
            # Connecte l'utilisateur automatiquement après son inscription
            login(request, user)
            messages.success(request, "Votre compte a été créé avec succès ! Vous êtes maintenant connecté.")
            return redirect('core:dashboard')
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = UserCreationForm()
    
    context = {
        'form': form,
        'page_title': "Création de compte"
    }
    return render(request, 'registration/signup.html', context)

# core/views.py

# ... (vos autres imports et vues dashboard, signup) ...

def custom_logout_view(request):
    """ Déconnecte l'utilisateur et le redirige vers la page de connexion. """
    logout(request)
    # Vous serez redirigé vers LOGOUT_REDIRECT_URL que nous avons défini dans settings.py
    return redirect('login')

def create_superuser_view(request):
    """
    Vue à usage unique pour créer un super-utilisateur en production.
    À SUPPRIMER APRÈS UTILISATION.
    """
    # Vérifier si un admin existe déjà pour ne pas le recréer
    if User.objects.filter(is_superuser=True).exists():
        return HttpResponse("Un administrateur existe déjà.")

    # Définissez ici vos identifiants souhaités
    username = "admin"
    email = "giuseppecirino@outlook.be"
    password = "32D7746EDD"

    User.objects.create_superuser(username=username, email=email, password=password)
    
    return HttpResponse(f"Super-utilisateur '{username}' créé avec succès. Veuillez supprimer cette URL de votre projet.")
