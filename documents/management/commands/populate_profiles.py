# documents/management/commands/populate_profiles.py

from django.core.management.base import BaseCommand
from django.db import transaction
from documents.models import Invoice, Quote, CreditNote

class Command(BaseCommand):
    help = "Popule le nouveau champ company_profile à partir de l'ancien champ user pour les documents existants."

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Début du script de population..."))

        # Pour les factures
        invoices_to_update = Invoice.objects.filter(company_profile__isnull=True)
        self.stdout.write(f"Traitement de {invoices_to_update.count()} factures...")
        for inv in invoices_to_update:
            if hasattr(inv, 'user') and inv.user and hasattr(inv.user, 'company_profile'):
                inv.company_profile = inv.user.company_profile
                inv.save(update_fields=['company_profile'])

        # Pour les devis
        quotes_to_update = Quote.objects.filter(company_profile__isnull=True)
        self.stdout.write(f"Traitement de {quotes_to_update.count()} devis...")
        for q in quotes_to_update:
            if hasattr(q, 'user') and q.user and hasattr(q.user, 'company_profile'):
                q.company_profile = q.user.company_profile
                q.save(update_fields=['company_profile'])

        # Pour les notes de crédit
        notes_to_update = CreditNote.objects.filter(company_profile__isnull=True)
        self.stdout.write(f"Traitement de {notes_to_update.count()} notes de crédit...")
        for n in notes_to_update:
            if hasattr(n, 'user') and n.user and hasattr(n.user, 'company_profile'):
                n.company_profile = n.user.company_profile
                n.save(update_fields=['company_profile'])

        self.stdout.write(self.style.SUCCESS("Script terminé avec succès !"))