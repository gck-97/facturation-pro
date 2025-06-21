import json
from datetime import timedelta

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.db import transaction
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from products.models import Product
from .models import Invoice, InvoiceItem, Quote, QuoteItem, Payment, CreditNote, CreditNoteItem, Client
from .forms import QuoteForm, QuoteItemFormset, InvoiceForm, InvoiceItemFormset
from .utils import generate_invoice_pdf, generate_quote_pdf, generate_credit_note_pdf

# --- Vues pour les Factures (Invoices) ---

@login_required
def invoice_list(request):
    invoices = Invoice.objects.filter(user=request.user).order_by('-issue_date', '-invoice_number')
    context = {
        'invoices_list': invoices,
        'page_title': 'Liste de vos Factures'
    }
    return render(request, 'documents/invoice_list.html', context)

@login_required
def invoice_detail(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id, user=request.user)
    context = {
        'invoice': invoice,
        'page_title': f"Détails Facture N°{invoice.invoice_number}"
    }
    return render(request, 'documents/invoice_detail.html', context)

@login_required
def view_invoice_pdf(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id, user=request.user)
    company_profile = request.user.company_profile
    pdf_content = generate_invoice_pdf(invoice, company_profile)
    response = HttpResponse(pdf_content, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="facture_{invoice.invoice_number}.pdf"'
    return response

# --- Vues pour les Devis (Quotes) ---

@login_required
def quote_list(request):
    quotes = Quote.objects.filter(user=request.user).order_by('-issue_date', '-quote_number')
    context = {
        'quotes_list': quotes,
        'page_title': 'Liste de vos Devis'
    }
    return render(request, 'documents/quote_list.html', context)

@login_required
def quote_detail(request, quote_id):
    quote = get_object_or_404(Quote, id=quote_id, user=request.user)
    context = {
        'quote': quote,
        'page_title': f"Détails Devis N°{quote.quote_number}"
    }
    return render(request, 'documents/quote_detail.html', context)

@login_required
def view_quote_pdf(request, quote_id):
    quote = get_object_or_404(Quote, id=quote_id, user=request.user)
    company_profile = request.user.company_profile
    pdf_content = generate_quote_pdf(quote, company_profile)
    response = HttpResponse(pdf_content, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="devis_{quote.quote_number}.pdf"'
    return response

@login_required
def quote_create(request):
    page_title = 'Créer un nouveau devis'
    products = Product.objects.filter(user=request.user)
    products_data = {str(p.id): {'description': p.description or '', 'price': str(p.prix_unitaire)} for p in products}

    if request.method == 'POST':
        form = QuoteForm(request.POST, user=request.user)
        formset = QuoteItemFormset(request.POST, prefix='items')
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                quote = form.save(commit=False)
                quote.user = request.user
                quote.save()
                formset.instance = quote
                formset.save()
            messages.success(request, f"Le devis N°{quote.quote_number} a été créé avec succès !")
            return redirect('documents:quote_detail', quote_id=quote.id)
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
    else:
        form = QuoteForm(user=request.user)
        formset = QuoteItemFormset(queryset=QuoteItem.objects.none(), prefix='items', form_kwargs={'user': request.user})

    context = {
        'form': form,
        'formset': formset,
        'page_title': page_title,
        'products_data_json': json.dumps(products_data),
        'document_type': 'quote'
    }
    return render(request, 'documents/document_form.html', context)

# --- Vues pour les Notes de Crédit (Credit Notes) ---

@login_required
def credit_note_list(request):
    credit_notes = CreditNote.objects.filter(user=request.user).order_by('-issue_date', '-credit_note_number')
    context = {
        'credit_notes_list': credit_notes,
        'page_title': 'Liste des Notes de Crédit'
    }
    return render(request, 'documents/credit_note_list.html', context)

@login_required
def credit_note_detail(request, credit_note_id):
    credit_note = get_object_or_404(CreditNote, id=credit_note_id, user=request.user)
    context = {
        'credit_note': credit_note,
        'page_title': f"Détails Note de Crédit N°{credit_note.credit_note_number}"
    }
    return render(request, 'documents/credit_note_detail.html', context)

@login_required
def view_credit_note_pdf(request, credit_note_id):
    credit_note = get_object_or_404(CreditNote, id=credit_note_id, user=request.user)
    company_profile = request.user.company_profile
    pdf_content = generate_credit_note_pdf(credit_note, company_profile)
    response = HttpResponse(pdf_content, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="note_de_credit_{credit_note.credit_note_number}.pdf"'
    return response

# --- Vues pour les Actions (Conversions) ---

@login_required
def convert_quote_to_invoice(request, quote_id):
    quote = get_object_or_404(Quote, id=quote_id, user=request.user)
    if quote.status != Quote.QuoteStatus.ACCEPTED:
        messages.error(request, "Seuls les devis acceptés peuvent être convertis en facture.")
        return redirect('documents:quote_detail', quote_id=quote.id)
    try:
        new_invoice = Invoice.objects.create(
            user=request.user,
            client=quote.client,
            issue_date=timezone.now().date(),
            due_date=timezone.now().date() + timedelta(days=30),
            status=Invoice.InvoiceStatus.DRAFT,
            vat_percentage=quote.vat_percentage,
            notes=f"Facture générée à partir du devis N°{quote.quote_number}.\n{quote.notes or ''}"
        )
        for item in quote.items.all():
            InvoiceItem.objects.create(
                invoice=new_invoice, product=item.product, description=item.description,
                quantity=item.quantity, unit_price_htva=item.unit_price_htva
            )
        new_invoice.update_totals()
        new_invoice.save(update_fields=['total_amount_htva', 'total_amount_ttc'])
        quote.status = Quote.QuoteStatus.CONVERTED
        quote.save(update_fields=['status', 'updated_at'])
        messages.success(request, f"Le devis N°{quote.quote_number} a été converti avec succès en Facture N°{new_invoice.invoice_number}.")
        return redirect('documents:invoice_detail', invoice_id=new_invoice.id)
    except Exception as e:
        messages.error(request, f"Une erreur est survenue lors de la conversion du devis : {e}")
        return redirect('documents:quote_detail', quote_id=quote.id)

@login_required
def create_credit_note_from_invoice(request, invoice_id):
    original_invoice = get_object_or_404(Invoice, id=invoice_id, user=request.user)
    if CreditNote.objects.filter(original_invoice=original_invoice, user=request.user).exists():
        messages.warning(request, f"Une note de crédit existe déjà pour la facture {original_invoice.invoice_number}.")
        existing_credit_note = CreditNote.objects.get(original_invoice=original_invoice, user=request.user)
        return redirect('documents:credit_note_detail', credit_note_id=existing_credit_note.id)
    try:
        new_credit_note = CreditNote.objects.create(
            user=request.user, client=original_invoice.client, original_invoice=original_invoice,
            issue_date=timezone.now().date(), status=CreditNote.CreditNoteStatus.DRAFT,
            vat_percentage=original_invoice.vat_percentage,
            notes=f"Note de crédit concernant la facture N°{original_invoice.invoice_number}."
        )
        for item in original_invoice.items.all():
            CreditNoteItem.objects.create(
                credit_note=new_credit_note, product=item.product, description=item.description,
                quantity=item.quantity, unit_price_htva=item.unit_price_htva
            )
        new_credit_note.update_totals()
        new_credit_note.save(update_fields=['total_amount_htva', 'total_amount_ttc'])
        messages.success(request, f"La note de crédit N°{new_credit_note.credit_note_number} a été créée avec succès.")
        return redirect('documents:credit_note_detail', credit_note_id=new_credit_note.id)
    except Exception as e:
        messages.error(request, f"Une erreur est survenue lors de la création de la note de crédit : {e}")
        return redirect('documents:invoice_detail', invoice_id=original_invoice.id)

@login_required
def invoice_create(request):
    page_title = 'Créer une nouvelle facture'
    products = Product.objects.filter(user=request.user)
    products_data = {str(p.id): {'description': p.description or '', 'price': str(p.prix_unitaire)} for p in products}

    if request.method == 'POST':
        form = InvoiceForm(request.POST, user=request.user)
        formset = InvoiceItemFormset(request.POST, prefix='items')
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                invoice = form.save(commit=False)
                invoice.user = request.user
                invoice.save()
                formset.instance = invoice
                formset.save()
            messages.success(request, f"La facture N°{invoice.invoice_number} a été créée avec succès !")
            return redirect('documents:invoice_detail', invoice_id=invoice.id)
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
    else:
        form = InvoiceForm(user=request.user)
        formset = InvoiceItemFormset(queryset=InvoiceItem.objects.none(), prefix='items', form_kwargs={'user': request.user})

    context = {
        'form': form,
        'formset': formset,
        'page_title': page_title,
        'products_data_json': json.dumps(products_data),
        'document_type': 'invoice'
    }
    return render(request, 'documents/document_form.html', context)

# --- Vues pour mettre à jour le statut des documents ---

@login_required
def update_invoice_status(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id, user=request.user)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        # Correction ici !
        if new_status in Invoice.InvoiceStatus.values:
            invoice.status = new_status
            invoice.save()
            messages.success(request, f"Le statut de la facture N°{invoice.invoice_number} a été mis à jour.")
        else:
            messages.error(request, "Statut invalide.")
        return redirect('documents:invoice_detail', invoice_id=invoice.id)

@login_required
def update_quote_status(request, quote_id):
    quote = get_object_or_404(Quote, id=quote_id, user=request.user)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in Quote.QuoteStatus.values:
            quote.status = new_status
            quote.save()
            messages.success(request, f"Le statut du devis N°{quote.quote_number} a été mis à jour.")
        else:
            messages.error(request, "Statut invalide.")
        return redirect('documents:quote_detail', quote_id=quote.id)

@login_required
def update_credit_note_status(request, credit_note_id):
    credit_note = get_object_or_404(CreditNote, id=credit_note_id, user=request.user)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in CreditNote.CreditNoteStatus.values:
            credit_note.status = new_status
            credit_note.save()
            messages.success(request, f"Le statut de la note de crédit N°{credit_note.credit_note_number} a été mis à jour.")
        else:
            messages.error(request, "Statut invalide.")
        return redirect('documents:credit_note_detail', credit_note_id=credit_note.id)
