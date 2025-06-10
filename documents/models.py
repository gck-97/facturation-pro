# documents/models.py

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from clients.models import Client
from products.models import Product
from django.db.models import Max, Sum

class Invoice(models.Model):
    # ... (cette classe reste inchangée) ...
    class InvoiceStatus(models.TextChoices):
        DRAFT = 'Brouillon', 'Brouillon'
        SENT = 'Envoyée', 'Envoyée'
        PAID = 'Payée', 'Payée'
        OVERDUE = 'En retard', 'En retard'
        CANCELLED = 'Annulée', 'Annulée'
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invoices')
    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name='invoices', help_text="Client associé à cette facture")
    invoice_number = models.CharField(max_length=50, blank=True, help_text="Numéro de facture unique par utilisateur (sera auto-généré si laissé vide)")
    issue_date = models.DateField(default=timezone.now, help_text="Date d'émission de la facture")
    due_date = models.DateField(help_text="Date d'échéance de la facture")
    status = models.CharField(max_length=10, choices=InvoiceStatus.choices, default=InvoiceStatus.DRAFT, help_text="Statut actuel de la facture")
    vat_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=21.00, help_text="Pourcentage de TVA appliqué (ex: 21.00)")
    total_amount_htva = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, blank=True, help_text="Montant total HTVA (calculé)")
    total_amount_ttc = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, blank=True, help_text="Montant total TTC (calculé)")
    notes = models.TextField(blank=True, null=True, help_text="Notes ou termes additionnels")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-issue_date', '-invoice_number']
        unique_together = ('user', 'invoice_number')
    def __str__(self):
        return f"Facture N°{self.invoice_number} - {self.client.nom} (User: {self.user.username})"
    @property
    def get_total_paid(self):
        total_paid = self.payments.all().aggregate(total=Sum('amount_paid'))['total'] or 0
        return total_paid
    @property
    def balance_due(self):
        return self.total_amount_ttc - self.get_total_paid
    def update_status_based_on_payments(self):
        if self.status == self.InvoiceStatus.CANCELLED:
            return
        total_paid = self.get_total_paid
        if total_paid >= self.total_amount_ttc:
            self.status = self.InvoiceStatus.PAID
        elif total_paid == 0 and self.due_date < timezone.now().date():
             self.status = self.InvoiceStatus.OVERDUE
        self.save(update_fields=['status'])
    @property
    def vat_amount(self):
        if self.total_amount_htva is not None and self.vat_percentage is not None:
            return (self.total_amount_htva * self.vat_percentage) / 100
        return 0
    def get_next_invoice_number(self):
        if not self.user_id:
            return None
        current_year = timezone.now().year
        last_invoice = Invoice.objects.filter(user=self.user, invoice_number__startswith=f"{current_year}-").aggregate(Max('invoice_number'))
        last_number_str = last_invoice.get('invoice_number__max')
        if last_number_str:
            try:
                last_sequence = int(last_number_str.split('-')[-1])
                next_sequence = last_sequence + 1
            except (ValueError, IndexError):
                next_sequence = 1
        else:
            next_sequence = 1
        return f"{current_year}-{str(next_sequence).zfill(4)}"
    def update_totals(self):
        aggregation = self.items.all().aggregate(total_sum=Sum('total_line_htva'))
        calculated_htva = aggregation.get('total_sum') or 0.00
        self.total_amount_htva = calculated_htva
        if self.total_amount_htva is not None and self.vat_percentage is not None:
            vat_amount_calc = (self.total_amount_htva * self.vat_percentage) / 100
            self.total_amount_ttc = self.total_amount_htva + vat_amount_calc
        else:
            self.total_amount_ttc = self.total_amount_htva
    def save(self, *args, **kwargs):
        if not self.invoice_number and self.user_id:
            self.invoice_number = self.get_next_invoice_number()
        if self.pk:
             self.update_totals()
        super().save(*args, **kwargs)

class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items', help_text="Facture à laquelle cet article appartient")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, blank=True, null=True, help_text="Produit/Service facturé (optionnel)")
    description = models.CharField(max_length=255)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price_htva = models.DecimalField(max_digits=10, decimal_places=2)
    total_line_htva = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    class Meta:
        ordering = ['id']
    def __str__(self):
        # MODIFIÉ: Logique plus sûre
        display_name = self.description
        if not display_name and self.product:
            display_name = self.product.nom
        return f"{self.quantity} x {display_name}"
    def save(self, *args, **kwargs):
        if self.product and not self.description:
            self.description = self.product.nom
        if self.product and self.unit_price_htva is None:
            self.unit_price_htva = self.product.prix_unitaire
        if self.quantity is not None and self.unit_price_htva is not None:
            self.total_line_htva = self.quantity * self.unit_price_htva
        else:
            self.total_line_htva = 0 
        super().save(*args, **kwargs)
        if self.invoice:
            self.invoice.update_totals()
            self.invoice.save(update_fields=['total_amount_htva', 'total_amount_ttc'])

class Quote(models.Model):
    # ... (cette classe reste inchangée) ...
    class QuoteStatus(models.TextChoices):
        DRAFT = 'Brouillon', 'Brouillon'
        SENT = 'Envoyé', 'Envoyé'
        ACCEPTED = 'Accepté', 'Accepté'
        DECLINED = 'Refusé', 'Refusé'
        EXPIRED = 'Expiré', 'Expiré'
        CONVERTED = 'Converti', 'Converti en Facture'
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quotes')
    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name='quotes', help_text="Client associé à ce devis")
    quote_number = models.CharField(max_length=50, blank=True, help_text="Numéro de devis unique par utilisateur (sera auto-généré si laissé vide)")
    issue_date = models.DateField(default=timezone.now, help_text="Date d'émission du devis")
    expiry_date = models.DateField(help_text="Date d'expiration du devis (validité)")
    status = models.CharField(max_length=10, choices=QuoteStatus.choices, default=QuoteStatus.DRAFT, help_text="Statut actuel du devis")
    vat_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=21.00, help_text="Pourcentage de TVA appliqué (ex: 21.00)")
    total_amount_htva = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, blank=True, help_text="Montant total HTVA (calculé)")
    total_amount_ttc = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, blank=True, help_text="Montant total TTC (calculé)")
    notes = models.TextField(blank=True, null=True, help_text="Termes ou notes spécifiques au devis")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-issue_date', '-quote_number']
        verbose_name = "Devis"
        verbose_name_plural = "Devis"
        unique_together = ('user', 'quote_number')
    def __str__(self):
        return f"Devis N°{self.quote_number} - {self.client.nom} (User: {self.user.username})"
    @property
    def vat_amount(self):
        if self.total_amount_htva is not None and self.vat_percentage is not None:
            return (self.total_amount_htva * self.vat_percentage) / 100
        return 0
    def get_next_quote_number(self):
        if not self.user_id:
            return None
        current_year = timezone.now().year
        prefix = f"DEV-{current_year}-"
        last_quote = Quote.objects.filter(user=self.user, quote_number__startswith=prefix).aggregate(Max('quote_number'))
        last_number_str = last_quote.get('quote_number__max')
        if last_number_str:
            try:
                last_sequence = int(last_number_str.split('-')[-1])
                next_sequence = last_sequence + 1
            except (ValueError, IndexError):
                next_sequence = 1
        else:
            next_sequence = 1
        return f"{prefix}{str(next_sequence).zfill(4)}"
    def update_totals(self):
        aggregation = self.items.all().aggregate(total_sum=Sum('total_line_htva'))
        calculated_htva = aggregation.get('total_sum') or 0.00
        self.total_amount_htva = calculated_htva
        if self.total_amount_htva is not None and self.vat_percentage is not None:
            vat_amount_calc = (self.total_amount_htva * self.vat_percentage) / 100
            self.total_amount_ttc = self.total_amount_htva + vat_amount_calc
        else:
            self.total_amount_ttc = self.total_amount_htva
    def save(self, *args, **kwargs):
        if not self.quote_number and self.user_id:
            self.quote_number = self.get_next_quote_number()
        if self.pk:
             self.update_totals()
        super().save(*args, **kwargs)

class QuoteItem(models.Model):
    quote = models.ForeignKey(Quote, on_delete=models.CASCADE, related_name='items', help_text="Devis auquel cet article appartient")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, blank=True, null=True, help_text="Produit/Service proposé (optionnel)")
    description = models.CharField(max_length=255, blank=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price_htva = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total_line_htva = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    class Meta:
        ordering = ['id']
        verbose_name = "Ligne de Devis"
        verbose_name_plural = "Lignes de Devis"
    def __str__(self):
        # MODIFIÉ: Logique plus sûre
        display_name = self.description
        if not display_name and self.product:
            display_name = self.product.nom
        return f"{self.quantity} x {display_name}"
    def save(self, *args, **kwargs):
        if self.product:
            if not self.description:
                self.description = self.product.nom
            if self.unit_price_htva is None:
                self.unit_price_htva = self.product.prix_unitaire
        if self.quantity is not None and self.unit_price_htva is not None:
            self.total_line_htva = self.quantity * self.unit_price_htva
        else:
            self.total_line_htva = 0 
        super().save(*args, **kwargs)
        if self.quote:
            self.quote.update_totals()
            self.quote.save(update_fields=['total_amount_htva', 'total_amount_ttc'])

class Payment(models.Model):
    # ... (cette classe reste inchangée) ...
    class PaymentMethod(models.TextChoices):
        BANK_TRANSFER = 'Virement', 'Virement bancaire'
        CARD = 'Carte', 'Carte de crédit'
        CASH = 'Especes', 'Espèces'
        OTHER = 'Autre', 'Autre'
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments', help_text="Facture associée à ce paiement")
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Montant payé")
    payment_date = models.DateField(default=timezone.now, verbose_name="Date du paiement")
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices, default=PaymentMethod.BANK_TRANSFER, verbose_name="Méthode de paiement")
    reference = models.CharField(max_length=255, blank=True, null=True, verbose_name="Référence ou note")
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-payment_date']
        verbose_name = "Paiement"
        verbose_name_plural = "Paiements"
    def __str__(self):
        return f"Paiement de {self.amount_paid} € pour la facture {self.invoice.invoice_number} le {self.payment_date}"
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.invoice.update_status_based_on_payments()

class CreditNote(models.Model):
    # ... (cette classe reste inchangée) ...
    class CreditNoteStatus(models.TextChoices):
        DRAFT = 'Brouillon', 'Brouillon'
        FINALIZED = 'Finalisée', 'Finalisée'
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='credit_notes')
    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name='credit_notes')
    original_invoice = models.ForeignKey(Invoice, on_delete=models.SET_NULL, null=True, blank=True, related_name='credit_notes')
    credit_note_number = models.CharField(max_length=50, unique=True, blank=True, help_text="Numéro de la note de crédit (sera auto-généré si laissé vide)")
    issue_date = models.DateField(default=timezone.now, help_text="Date d'émission de la note de crédit")
    status = models.CharField(max_length=10, choices=CreditNoteStatus.choices, default=CreditNoteStatus.DRAFT)
    vat_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=21.00)
    total_amount_htva = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, blank=True)
    total_amount_ttc = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, blank=True)
    notes = models.TextField(blank=True, null=True, help_text="Raison de la note de crédit ou autres notes")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-issue_date', '-credit_note_number']
        verbose_name = "Note de Crédit"
        verbose_name_plural = "Notes de Crédit"
        unique_together = ('user', 'credit_note_number')
    def __str__(self):
        return f"Note de Crédit N°{self.credit_note_number} - {self.client.nom}"
    @property
    def vat_amount(self):
        if self.total_amount_htva is not None and self.vat_percentage is not None:
            return (self.total_amount_htva * self.vat_percentage) / 100
        return 0
    def get_next_credit_note_number(self):
        if not self.user_id:
            return None
        current_year = timezone.now().year
        prefix = f"NC-{current_year}-"
        last_credit_note = CreditNote.objects.filter(user=self.user, credit_note_number__startswith=prefix).aggregate(Max('credit_note_number'))
        last_number_str = last_credit_note.get('credit_note_number__max')
        if last_number_str:
            try:
                last_sequence = int(last_number_str.split('-')[-1])
                next_sequence = last_sequence + 1
            except (ValueError, IndexError):
                next_sequence = 1
        else:
            next_sequence = 1
        return f"{prefix}{str(next_sequence).zfill(4)}"
    def update_totals(self):
        aggregation = self.items.all().aggregate(total_sum=Sum('total_line_htva'))
        calculated_htva = aggregation.get('total_sum') or 0.00
        self.total_amount_htva = calculated_htva
        if self.total_amount_htva is not None and self.vat_percentage is not None:
            vat_amount_calc = (self.total_amount_htva * self.vat_percentage) / 100
            self.total_amount_ttc = self.total_amount_htva + vat_amount_calc
        else:
            self.total_amount_ttc = self.total_amount_htva
    def save(self, *args, **kwargs):
        if not self.credit_note_number and self.user_id:
            self.credit_note_number = self.get_next_credit_note_number()
        if self.pk:
             self.update_totals()
        super().save(*args, **kwargs)

class CreditNoteItem(models.Model):
    credit_note = models.ForeignKey(CreditNote, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price_htva = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total_line_htva = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    class Meta:
        verbose_name = "Ligne de Note de Crédit"
        verbose_name_plural = "Lignes de Note de Crédit"
    def __str__(self):
        # MODIFIÉ: Logique plus sûre
        display_name = self.description
        if not display_name and self.product:
            display_name = self.product.nom
        return f"{self.quantity} x {display_name}"
    def save(self, *args, **kwargs):
        if self.product:
            if not self.description:
                self.description = self.product.nom
            if self.unit_price_htva is None:
                self.unit_price_htva = self.product.prix_unitaire
        if self.quantity is not None and self.unit_price_htva is not None:
            self.total_line_htva = self.quantity * self.unit_price_htva
        else:
            self.total_line_htva = 0 
        super().save(*args, **kwargs)
        if self.credit_note:
            self.credit_note.update_totals()
            self.credit_note.save(update_fields=['total_amount_htva', 'total_amount_ttc'])