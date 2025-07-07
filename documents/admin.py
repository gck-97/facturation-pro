from django.contrib import admin, messages
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.html import format_html

from .models import Invoice, InvoiceItem, Quote, QuoteItem, Payment, CreditNote, CreditNoteItem
from clients.models import Client

# --- Inlines ---

class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1
    fields = ('product', 'description', 'quantity', 'unit_price_htva', 'total_line_htva')
    readonly_fields = ('total_line_htva',)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "product":
            if request.user and not request.user.is_superuser:
                kwargs["queryset"] = db_field.related_model.objects.filter(user=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 1
    fields = ('payment_date', 'amount_paid', 'payment_method', 'reference')

class QuoteItemInline(admin.TabularInline):
    model = QuoteItem
    extra = 1
    fields = ('product', 'description', 'quantity', 'unit_price_htva', 'total_line_htva')
    readonly_fields = ('total_line_htva',)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "product":
            if request.user and not request.user.is_superuser:
                kwargs["queryset"] = db_field.related_model.objects.filter(user=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

class CreditNoteItemInline(admin.TabularInline):
    model = CreditNoteItem
    extra = 1
    fields = ('product', 'description', 'quantity', 'unit_price_htva', 'total_line_htva')
    readonly_fields = ('total_line_htva',)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "product":
            if request.user and not request.user.is_superuser:
                kwargs["queryset"] = db_field.related_model.objects.filter(user=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

# --- ADMIN PRINCIPAL ---

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = (
        'invoice_number', 'client', 'issue_date', 'status',
        'total_amount_ttc', 'balance_due', 'user', 'download_pdf_link'
    )
    list_filter = ('status', 'issue_date', 'user')
    search_fields = ('invoice_number', 'client__nom')
    date_hierarchy = 'issue_date'
    inlines = [InvoiceItemInline, PaymentInline]
    actions = ['send_invoice_email']

    fieldsets = (
        (None, {'fields': ('client', 'status')}),
        ('Dates', {'fields': ('issue_date', 'due_date')}),
        ('Montants et TVA', {'fields': ('vat_percentage', 'total_amount_htva', 'total_amount_ttc', 'balance_due')}),
        ('Notes additionnelles', {'fields': ('notes',), 'classes': ('collapse',)}),
        ('Lien PDF', {'fields': ('invoice_pdf_display_link',)}),
    )
    readonly_fields = ('total_amount_htva', 'total_amount_ttc', 'balance_due', 'invoice_pdf_display_link')

    def balance_due(self, obj):
        return f"{obj.balance_due:.2f} €"
    balance_due.short_description = "Solde Restant Dû"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.user = request.user
        super().save_model(request, obj, form, change)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "client":
            if request.user and not request.user.is_superuser:
                kwargs["queryset"] = Client.objects.filter(user=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def invoice_pdf_display_link(self, obj):
        if obj.pk:
            url = reverse('documents:view_invoice_pdf', args=[obj.pk])
            return format_html('<a href="{}" target="_blank">Télécharger / Voir PDF</a>', url)
        return "N/A (Sauvegardez d'abord pour générer le lien PDF)"
    invoice_pdf_display_link.short_description = 'Document PDF'

    def download_pdf_link(self, obj):
        if obj.pk:
            url = reverse('documents:view_invoice_pdf', args=[obj.pk])
            return format_html('<a href="{}" target="_blank">PDF</a>', url)
        return "N/A"
    download_pdf_link.short_description = 'PDF'

    # ACTION pour envoyer par mail
    def send_invoice_email(self, request, queryset):
        sent = 0
        for invoice in queryset:
            if not invoice.client.email:
                self.message_user(
                    request,
                    f"Le client '{invoice.client}' n'a pas d'adresse email.",
                    level=messages.WARNING
                )
                continue
            public_url = request.build_absolute_uri(
                reverse('documents:invoice_public_view', args=[invoice.public_token])
            )
            send_mail(
                subject=f"Votre facture {invoice.invoice_number}",
                message=(
                    f"Bonjour,\n\nVeuillez trouver votre facture en ligne : {public_url}\n\n"
                    "Merci pour votre confiance !"
                ),
                from_email=None,  # Utilise DEFAULT_FROM_EMAIL du settings.py
                recipient_list=[invoice.client.email],
                fail_silently=False,
            )
            sent += 1
        self.message_user(request, f"{sent} email(s) envoyé(s) !", level=messages.SUCCESS)
    send_invoice_email.short_description = "Envoyer la facture par email au client"

@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = ('quote_number', 'client', 'issue_date', 'status', 'total_amount_ttc', 'user')
    list_filter = ('status', 'issue_date', 'user')
    search_fields = ('quote_number', 'client__nom')
    date_hierarchy = 'issue_date'
    inlines = [QuoteItemInline]
    fieldsets = (
        (None, {'fields': ('client', 'status')}),
        ('Dates Importantes', {'fields': ('issue_date', 'expiry_date')}),
        ('Montants et TVA', {'fields': ('vat_percentage', 'total_amount_htva', 'total_amount_ttc')}),
        ('Notes', {'fields': ('notes',), 'classes': ('collapse',)}),
    )
    readonly_fields = ('total_amount_htva', 'total_amount_ttc')
    actions = ['send_quote_email']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.user = request.user
        super().save_model(request, obj, form, change)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "client":
            if request.user and not request.user.is_superuser:
                kwargs["queryset"] = Client.objects.filter(user=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    # ACTION pour envoyer le devis par mail
    def send_quote_email(self, request, queryset):
        sent = 0
        for quote in queryset:
            if not quote.client.email:
                self.message_user(
                    request,
                    f"Le client '{quote.client}' n'a pas d'adresse email.",
                    level=messages.WARNING
                )
                continue
            public_url = request.build_absolute_uri(
                reverse('documents:quote_public_view', args=[quote.public_token])
            )
            send_mail(
                subject=f"Votre devis {quote.quote_number}",
                message=(
                    f"Bonjour,\n\nVeuillez trouver votre devis en ligne : {public_url}\n\n"
                    "N'hésitez pas à nous contacter pour toute question.\n\nMerci pour votre confiance !"
                ),
                from_email=None,  # Utilise DEFAULT_FROM_EMAIL du settings.py
                recipient_list=[quote.client.email],
                fail_silently=False,
            )
            sent += 1
        self.message_user(request, f"{sent} email(s) de devis envoyé(s) !", level=messages.SUCCESS)
    send_quote_email.short_description = "Envoyer le devis par email au client"

@admin.register(CreditNote)
class CreditNoteAdmin(admin.ModelAdmin):
    list_display = (
        'credit_note_number', 'client', 'issue_date', 'status',
        'total_amount_ttc', 'user', 'download_credit_note_pdf_link'
    )
    list_filter = ('status', 'issue_date', 'user')
    search_fields = ('credit_note_number', 'client__nom', 'original_invoice__invoice_number')
    inlines = [CreditNoteItemInline]

    fieldsets = (
        (None, {'fields': ('client', 'status', 'original_invoice')}),
        ('Dates', {'fields': ('issue_date',)}),
        ('Montants et TVA', {'fields': ('vat_percentage', 'total_amount_htva', 'total_amount_ttc')}),
        ('Notes', {'fields': ('notes',), 'classes': ('collapse',)}),
    )
    readonly_fields = ('total_amount_htva', 'total_amount_ttc')
    actions = ['send_credit_note_email']

    def download_credit_note_pdf_link(self, obj):
        if obj.pk:
            url = reverse('documents:view_credit_note_pdf', args=[obj.pk])
            return format_html('<a href="{}" target="_blank">PDF</a>', url)
        return "N/A"
    download_credit_note_pdf_link.short_description = 'PDF Note de Crédit'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.user = request.user
        super().save_model(request, obj, form, change)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name in ["client", "original_invoice"]:
            if request.user and not request.user.is_superuser:
                kwargs["queryset"] = db_field.related_model.objects.filter(user=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    # ACTION pour envoyer la note de crédit par mail
    def send_credit_note_email(self, request, queryset):
        sent = 0
        for credit_note in queryset:
            if not credit_note.client.email:
                self.message_user(
                    request,
                    f"Le client '{credit_note.client}' n'a pas d'adresse email.",
                    level=messages.WARNING
                )
                continue
            public_url = request.build_absolute_uri(
                reverse('documents:view_credit_note_pdf', args=[credit_note.pk])
            )
            send_mail(
                subject=f"Votre note de crédit {credit_note.credit_note_number}",
                message=(
                    f"Bonjour,\n\nVeuillez trouver votre note de crédit ici : {public_url}\n\n"
                    "N'hésitez pas à nous contacter pour toute question.\n\nMerci pour votre confiance !"
                ),
                from_email=None,
                recipient_list=[credit_note.client.email],
                fail_silently=False,
            )
            sent += 1
        self.message_user(request, f"{sent} email(s) de note de crédit envoyé(s) !", level=messages.SUCCESS)
    send_credit_note_email.short_description = "Envoyer la note de crédit par email au client"
