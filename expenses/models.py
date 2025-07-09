from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone



User = get_user_model()

class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    label = models.CharField("Objet du frais", max_length=255)
    amount = models.DecimalField("Montant", max_digits=10, decimal_places=2)
    date = models.DateField("Date", auto_now_add=True)
    receipt = models.ImageField("Photo du justificatif", upload_to="receipts/", blank=True, null=True)

    def __str__(self):
        return f"{self.label} - {self.amount} €"
