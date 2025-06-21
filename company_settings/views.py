from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import CompanyProfile
from .forms import CompanyProfileForm
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from documents.utils import BasePDFGenerator
from io import BytesIO
from reportlab.lib.pagesizes import A4

@login_required
def manage_profile(request):
    profile, created = CompanyProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = CompanyProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('manage_profile')
    else:
        form = CompanyProfileForm(instance=profile)
    return render(request, 'company_settings/manage_profile.html', {
        'form': form,
        'profile': profile,
    })


@csrf_exempt  # OK pour l'aperçu, à sécuriser si prod publique
@login_required
def live_pdf_preview(request):
    """Génère dynamiquement un PDF APERCU fidèle au modèle de devis/facture/note de crédit."""
    if request.method == 'POST':
        user = request.user
        profile = user.company_profile

        def get_or(field, default=""):
            return request.POST.get(field, getattr(profile, field, default))

        class PreviewProfile:
            pass
        fake_profile = PreviewProfile()

        for field in [
            'company_name', 'address_line1', 'address_line2', 'postal_code', 'city', 'country',
            'vat_number', 'phone_number', 'email_address', 'accent_color', 'terms_and_conditions'
        ]:
            setattr(fake_profile, field, get_or(field))

        # Toujours garder le logo déjà enregistré (upload temporaire impossible sans enregistrer)
        fake_profile.logo = getattr(profile, 'logo', None)

        if fake_profile.accent_color and not str(fake_profile.accent_color).startswith('#'):
            fake_profile.accent_color = f"#{fake_profile.accent_color}"

        class DummyItem:
            def __init__(self, desc, qty, unit, total):
                self.description = desc
                self.quantity = qty
                self.unit_price_htva = unit
                self.total_line_htva = total

        class DummyItemsQuerysetLike(list):
            def all(self):
                return self

        class DummyDoc:
            def __init__(self, profile):
                from types import SimpleNamespace
                self.issue_date = self.due_date = self.expiry_date = timezone.now().date()
                self.quote_number = "APERCU"
                self.invoice_number = "APERCU"
                self.credit_note_number = "APERCU"
                self.vat_percentage = 21.0
                self.total_amount_htva = 100.00
                self.vat_amount = 21.00
                self.total_amount_ttc = 121.00
                self.notes = "Ceci est un aperçu de votre document."
                self.client = SimpleNamespace(
                    id=1, nom="Client Exemple",
                    adresse_ligne1="Rue du Test 42",
                    code_postal="1000", ville="Bruxelles",
                    telephone="0123456789", email="client@example.com"
                )
                self.items = DummyItemsQuerysetLike([
                    DummyItem("Prestation de test", 2, 50.00, 100.00)
                ])

        doc = DummyDoc(fake_profile)

        # Ici on passe fake_profile au générateur pour qu'il utilise les bonnes couleurs et logo
        buffer = BytesIO()
        generator = BasePDFGenerator(buffer, A4, company_profile=fake_profile)
        generator.build_pdf(doc, "DEVIS")
        pdf = buffer.getvalue()
        buffer.close()

        return HttpResponse(pdf, content_type="application/pdf")

    return HttpResponse(status=405)
