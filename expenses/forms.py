from django import forms
from .models import Expense

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['label', 'amount', 'receipt']
        widgets = {
            'label': forms.TextInput(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'receipt': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
