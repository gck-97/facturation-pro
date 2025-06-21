# settings/models.py
from django.db import models

class CompanyProfile(models.Model):
    company_name = models.CharField(max_length=255)
    address_line1 = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    email_address = models.EmailField(blank=True, null=True)
    vat_number = models.CharField(max_length=50, blank=True, null=True)
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    terms_and_conditions = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.company_name
