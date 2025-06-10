# documents/admin.py

from django.contrib import admin
# Assurez-vous d'importer tous vos modèles
from .models import Invoice, InvoiceItem, Quote, QuoteItem, Payment, CreditNote, CreditNoteItem
from clients.models import Client
from django.urls import reverse
from django.utils.html import format_html

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

# NOUVEL INLINE POUR LES LIGNES DE NOTE DE CRÉDIT
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


# --- Administrations des Modèles Principaux ---

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    # ... (votre code InvoiceAdmin existant, inchangé) ...
    list_display = ('invoice_number', 'client', 'issue_date', 'status', 'total_amount_ttc', 'balance_due', 'user', 'download_pdf_link')
    list_filter = ('status', 'issue_date', 'user')
    search_fields = ('invoice_number', 'client__nom')
    date_hierarchy = 'issue_date'
    inlines = [InvoiceItemInline, PaymentInline]
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


@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    # ... (votre code QuoteAdmin existant, inchangé) ...
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


# NOUVELLE CLASSE ADMIN POUR LES NOTES DE CRÉDIT
@admin.register(CreditNote)
class CreditNoteAdmin(admin.ModelAdmin):
    # MODIFIÉ: Ajout de 'download_credit_note_pdf_link'
    list_display = ('credit_note_number', 'client', 'issue_date', 'status', 'total_amount_ttc', 'user', 'download_credit_note_pdf_link')
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

    # NOUVELLE MÉTHODE pour le lien PDF
    def download_credit_note_pdf_link(self, obj):
        if obj.pk:
            url = reverse('documents:view_credit_note_pdf', args=[obj.pk])
            return format_html('<a href="{}" target="_blank">PDF</a>', url)
        return "N/A"
    download_credit_note_pdf_link.short_description = 'PDF Note de Crédit'

    # ... (le reste de votre CreditNoteAdmin : get_queryset, save_model, etc.) ...
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