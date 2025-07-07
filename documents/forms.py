from django import forms
from django.forms import inlineformset_factory
from .models import Quote, QuoteItem, Client, Product, Invoice, InvoiceItem, Payment

class QuoteForm(forms.ModelForm):
    class Meta:
        model = Quote
        fields = ['client', 'issue_date', 'expiry_date', 'vat_percentage', 'notes']
        widgets = {
            'client': forms.Select(attrs={'class': 'form-select client-select'}),
            'issue_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'expiry_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'vat_percentage': forms.NumberInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
        labels = {
            'client': "Choisir un client",
            'issue_date': "Date d'émission",
            'expiry_date': "Date d'expiration",
            'vat_percentage': "Taux de TVA (%)",
            'notes': "Notes additionnelles"
        }
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['client'].queryset = Client.objects.filter(user=user)

class QuoteItemForm(forms.ModelForm):
    class Meta:
        model = QuoteItem
        fields = ['product', 'description', 'quantity', 'unit_price_htva']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-select product-select'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control quantity', 'step': '0.01'}),
            'unit_price_htva': forms.NumberInput(attrs={'class': 'form-control price', 'step': '0.01'}),
        }
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['product'].queryset = Product.objects.filter(user=user)
        self.fields['product'].required = False

QuoteItemFormset = inlineformset_factory(
    Quote,
    QuoteItem,
    form=QuoteItemForm,
    extra=1,
    can_delete=True,
)

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['client', 'issue_date', 'due_date', 'vat_percentage', 'notes']
        widgets = {
            'client': forms.Select(attrs={'class': 'form-select client-select'}),
            'issue_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'due_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'vat_percentage': forms.NumberInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
        labels = {
            'client': "Choisir un client",
            'issue_date': "Date d'émission",
            'due_date': "Date d'échéance",
            'vat_percentage': "Taux de TVA (%)",
            'notes': "Notes additionnelles"
        }
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['client'].queryset = Client.objects.filter(user=user)

class InvoiceItemForm(forms.ModelForm):
    class Meta:
        model = InvoiceItem
        fields = ['product', 'description', 'quantity', 'unit_price_htva']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-select product-select'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control quantity', 'step': '0.01'}),
            'unit_price_htva': forms.NumberInput(attrs={'class': 'form-control price', 'step': '0.01'}),
        }
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['product'].queryset = Product.objects.filter(user=user)
        self.fields['product'].required = False

InvoiceItemFormset = inlineformset_factory(
    Invoice,
    InvoiceItem,
    form=InvoiceItemForm,
    extra=1,
    can_delete=True
)

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['amount_paid', 'payment_date', 'payment_method', 'reference']
        widgets = {
            'amount_paid': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'payment_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'payment_method': forms.Select(attrs={'class': 'form-select'}),
            'reference': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'amount_paid': 'Montant payé',
            'payment_date': 'Date du paiement',
            'payment_method': 'Méthode de paiement',
            'reference': 'Référence ou note'
        }
