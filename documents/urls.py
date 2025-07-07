from django.urls import path
from . import views

app_name = 'documents'

urlpatterns = [
    # Factures
    path('invoices/', views.invoice_list, name='invoice_list'),
    path('invoice/<int:invoice_id>/', views.invoice_detail, name='invoice_detail'),
    path('invoice/<int:invoice_id>/pdf/', views.view_invoice_pdf, name='view_invoice_pdf'),
    path('invoice/add/', views.invoice_create, name='invoice_create'),

    # Paiements
    path('invoice/<int:invoice_id>/ajax_add_payment/', views.ajax_add_payment, name='ajax_add_payment'),
    path('payment/<int:payment_id>/ajax_delete/', views.ajax_delete_payment, name='ajax_delete_payment'),

    # Changement de statut
    path('invoice/<int:invoice_id>/update_status/', views.update_invoice_status, name='update_invoice_status'),
    path('quote/<int:quote_id>/update_status/', views.update_quote_status, name='update_quote_status'),
    path('credit-note/<int:credit_note_id>/update_status/', views.update_credit_note_status, name='update_credit_note_status'),

    # Envoi email
    path('invoice/<int:invoice_id>/send_email/', views.send_invoice_email_view, name='send_invoice_email'),
    path('quote/<int:quote_id>/send_email/', views.send_quote_email_view, name='send_quote_email'),
    path('credit-note/<int:credit_note_id>/send_email/', views.send_credit_note_email_view, name='send_credit_note_email'),

    # Vue publique facture/devis
    path('invoice/public/<uuid:public_token>/', views.invoice_public_view, name='invoice_public_view'),
    path('invoice/public/<uuid:public_token>/pdf/', views.invoice_public_pdf, name='invoice_public_pdf'),
    path('quote/public/<uuid:public_token>/', views.quote_public_view, name='quote_public_view'),
    path('quote/public/<uuid:public_token>/pdf/', views.quote_public_pdf, name='quote_public_pdf'),

    # Devis
    path('quotes/', views.quote_list, name='quote_list'),
    path('quote/add/', views.quote_create, name='quote_create'),
    path('quote/<int:quote_id>/', views.quote_detail, name='quote_detail'),
    path('quote/<int:quote_id>/pdf/', views.view_quote_pdf, name='view_quote_pdf'),
    path('quote/<int:quote_id>/convert/', views.convert_quote_to_invoice, name='convert_quote_to_invoice'),

    # Notes de crédit
    path('credit-notes/', views.credit_note_list, name='credit_note_list'),
    path('credit-note/<int:credit_note_id>/', views.credit_note_detail, name='credit_note_detail'),
    path('credit-note/<int:credit_note_id>/pdf/', views.view_credit_note_pdf, name='view_credit_note_pdf'),
    path('invoice/<int:invoice_id>/create-credit-note/', views.create_credit_note_from_invoice, name='create_credit_note_from_invoice'),

    # Vues publiques pour note de crédit (optionnel, utile pour lien mail)
    path('credit-note/<int:credit_note_id>/public/pdf/', views.view_credit_note_pdf, name='credit_note_public_pdf'),

    path('quote/accept/<uuid:public_token>/', views.quote_accept_view, name='quote_accept'),
    path('quote/reject/<uuid:public_token>/', views.quote_reject_view, name='quote_reject'),

]
