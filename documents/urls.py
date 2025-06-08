# documents/urls.py

from django.urls import path
from . import views

app_name = 'documents'

urlpatterns = [
    path('invoices/', views.invoice_list, name='invoice_list'),
    path('invoice/<int:invoice_id>/', views.invoice_detail, name='invoice_detail'), # <-- NOUVELLE LIGNE
    path('invoice/<int:invoice_id>/pdf/', views.view_invoice_pdf, name='view_invoice_pdf'),

    # URLs pour les devis
    path('quote/<int:quote_id>/pdf/', views.view_quote_pdf, name='view_quote_pdf'),
    path('quotes/', views.quote_list, name='quote_list'),
    path('quote/add/', views.quote_create, name='quote_create'),
    path('quote/<int:quote_id>/', views.quote_detail, name='quote_detail'),

    # NOUVELLE URL pour la conversion devis -> facture
    path('quote/<int:quote_id>/convert/', views.convert_quote_to_invoice, name='convert_quote_to_invoice'),

     # NOUVELLE URL pour le PDF de la note de crédit
    path('credit-note/<int:credit_note_id>/pdf/', views.view_credit_note_pdf, name='view_credit_note_pdf'),
    path('credit-notes/', views.credit_note_list, name='credit_note_list'), # <-- NOUVELLE LIGNE
    path('credit-note/<int:credit_note_id>/', views.credit_note_detail, name='credit_note_detail'), # <-- NOUVELLE LIGNE

    # NOUVELLE URL pour générer une note de crédit à partir d'une facture
    path('invoice/<int:invoice_id>/create-credit-note/', views.create_credit_note_from_invoice, name='create_credit_note_from_invoice'),
]