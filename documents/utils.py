# documents/utils.py

from io import BytesIO
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT
from django.utils import timezone

from company_settings.models import CompanyProfile

class BasePDFGenerator:
    def __init__(self, buffer, pagesize):
        self.buffer = buffer
        self.pagesize = pagesize
        self.width, self.height = pagesize

        self.company_profile = CompanyProfile.objects.first()
        self.accent_color = colors.HexColor(self.company_profile.accent_color if self.company_profile and self.company_profile.accent_color else '#2c3e50')
        
        # --- Définition des Styles ---
        self.styles = getSampleStyleSheet()
        self.styles.add(ParagraphStyle(name='Normal_RIGHT', parent=self.styles['Normal'], alignment=TA_RIGHT))
        self.styles.add(ParagraphStyle(name='Normal_LEFT', parent=self.styles['Normal'], alignment=TA_LEFT))
        # Style du Titre du document (ex: FACTURE) en couleur
        self.styles.add(ParagraphStyle(name='DocTitle', parent=self.styles['h1'], fontSize=20, leading=24, textColor=self.accent_color))
        # Style du Numéro du document, en noir
        self.styles.add(ParagraphStyle(name='DocNumber', parent=self.styles['h1'], fontSize=20, leading=24, textColor=colors.black))
        # Style pour le titre "CLIENT N°..."
        self.styles.add(ParagraphStyle(name='SectionTitle', parent=self.styles['h2'], fontSize=12, leading=14, textColor=self.accent_color))
        # Style pour les infos de l'entreprise (texte en couleur, aligné à gauche DANS son bloc)
        self.styles.add(ParagraphStyle(name='CompanyInfo', parent=self.styles['Normal'], alignment=TA_LEFT, textColor=self.accent_color))
        # Styles pour les en-têtes du tableau des articles
        self.styles.add(ParagraphStyle(name='TableHeader', parent=self.styles['Normal'], fontName='Helvetica-Bold', textColor=self.accent_color, alignment=TA_LEFT))
        self.styles.add(ParagraphStyle(name='TableHeader_RIGHT', parent=self.styles['Normal'], fontName='Helvetica-Bold', textColor=self.accent_color, alignment=TA_RIGHT))

# Dans documents/utils.py, à l'intérieur de la classe BasePDFGenerator

    def _build_header_and_addresses(self, doc_type, doc_number, issue_date, other_date_label, other_date, client):
        """ Construit l'en-tête et les adresses avec la logique d'alignement finale et correcte. """
        
        # --- Colonne de gauche (Titre, Dates, Infos Client) ---
        title_text = Paragraph(doc_type.upper(), self.styles['DocTitle'])
        number_text = Paragraph(f"N° {doc_number}", self.styles['DocNumber'])
        dates_text = f"Date d'émission : {issue_date.strftime('%d/%m/%Y')}<br/>{other_date_label} : {other_date.strftime('%d/%m/%Y')}"
        
        client_title = Paragraph(f"CLIENT N°{client.id} :", self.styles['SectionTitle'])
        client_info_text = f"""
            {client.nom}<br/>
            {client.adresse_ligne1 or ''}<br/>
            {client.code_postal or ''} {client.ville or ''}<br/>
            Tél : {client.telephone or ''}<br/>
            Email : {client.email or ''}
        """
        left_col_content = [title_text, number_text, Spacer(1, 0.3*cm), Paragraph(dates_text, self.styles['Normal_LEFT']), Spacer(1, 1.5*cm), client_title, Spacer(1, 0.2*cm), Paragraph(client_info_text, self.styles['Normal_LEFT'])]

        # --- Colonne de droite (Logo et Infos Entreprise) ---
        right_col_content = []
        if self.company_profile:
            company_block_data = []
            if self.company_profile.logo:
                try:
                    img = Image(self.company_profile.logo.path, width=5*cm, height=2.5*cm, hAlign='RIGHT')
                    company_block_data.append([img])
                    company_block_data.append([Spacer(1, 0.2*cm)])
                except Exception:
                    pass
            
            company_info_text = f"""
                <strong>{self.company_profile.company_name or ''}</strong><br/>
                {self.company_profile.address_line1 or ''}<br/>
                {self.company_profile.postal_code or ''} {self.company_profile.city or ''}<br/>
                N° TVA : {self.company_profile.vat_number or ''}<br/>
                Tél : {self.company_profile.phone_number or ''}<br/>
                Email : {self.company_profile.email_address or ''}
            """
            company_info_paragraph = Paragraph(company_info_text, self.styles['CompanyInfo'])
            company_block_data.append([company_info_paragraph])
            
            company_block_table = Table(company_block_data, style=[('VALIGN', (0,0), (-1,-1), 'TOP')])
            right_col_content.append(company_block_table)

        # On crée la table principale à 2 colonnes
        main_header_data = [[left_col_content, right_col_content]]
        # MODIFICATION ICI pour changer la largeur des colonnes
        main_header_table = Table(main_header_data, colWidths=[self.width*0.6 - 2*cm, self.width*0.4 - 2*cm])
        main_header_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('ALIGN', (1,0), (1,0), 'RIGHT'),
        ]))
        
        return main_header_table

    def _build_items_and_totals_table(self, document):
        table_header = [
            Paragraph("Description", self.styles['TableHeader']), 
            Paragraph("Quantité", self.styles['TableHeader_RIGHT']), 
            Paragraph("PU (€)", self.styles['TableHeader_RIGHT']), 
            Paragraph("Total (€)", self.styles['TableHeader_RIGHT'])
        ]
        data_table = [table_header]

        for item in document.items.all():
            data_table.append([
                Paragraph(item.description, self.styles['Normal']),
                Paragraph(str(item.quantity), self.styles['Normal_RIGHT']),
                Paragraph(f"{item.unit_price_htva:.2f}", self.styles['Normal_RIGHT']),
                Paragraph(f"{item.total_line_htva:.2f}", self.styles['Normal_RIGHT'])
            ])
        
        data_table.append(['', '', '', '']) # Ligne vide pour espacement
        
        # Lignes des totaux
        htva_row = ['', '', Paragraph('Total HTVA :', self.styles['Normal_RIGHT']), f"{document.total_amount_htva:.2f} €"]
        vat_row = ['', '', Paragraph(f"TVA ({document.vat_percentage:.2f} %) :", self.styles['Normal_RIGHT']), f"{document.vat_amount:.2f} €"]
        ttc_row = ['', '', Paragraph('<strong>TOTAL TTC :</strong>', self.styles['Normal_RIGHT']), Paragraph(f'<strong>{document.total_amount_ttc:.2f} €</strong>', self.styles['Normal_RIGHT'])]
        
        data_table.extend([htva_row, vat_row, ttc_row])
        
        item_table = Table(data_table, colWidths=['*', 2*cm, 3*cm, 3*cm], repeatRows=1)
        
        item_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            # Ligne noire sous l'en-tête
            ('LINEBELOW', (0,0), (-1,0), 1, colors.black),
            # Ligne noire au-dessus des totaux
            ('LINEABOVE', (2,-3), (-1,-3), 1, colors.black),
            # Alignements
            ('ALIGN', (1,1), (-1,-1), 'RIGHT'),
            # Style de la ligne TOTAL TTC
            ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
        ]))
        
        return item_table
    
    def _build_footer(self, story):
        if self.company_profile and self.company_profile.terms_and_conditions:
            story.append(PageBreak())
            story.append(Paragraph("Conditions Générales", self.styles['h2']))
            story.append(Spacer(1, 0.5*cm))
            story.append(Paragraph(self.company_profile.terms_and_conditions.replace('\n', '<br/>'), self.styles['Normal']))

    def build_pdf(self, document, doc_type):
        story = []
        
        if doc_type == "FACTURE":
            doc_number_val, other_date_label, other_date = document.invoice_number, "Date d'échéance", document.due_date
        elif doc_type == "DEVIS":
            doc_number_val, other_date_label, other_date = document.quote_number, "Date d'expiration", document.expiry_date
        else: # NOTE DE CRÉDIT
            doc_number_val, other_date_label, other_date = document.credit_note_number, "Concerne la facture du", document.issue_date
        
        story.append(self._build_header_and_addresses(doc_type, doc_number_val, document.issue_date, other_date_label, other_date, document.client))
        story.append(Spacer(1, 1.5*cm))
        story.append(self._build_items_and_totals_table(document))
        self._build_footer(story)
        
        doc = SimpleDocTemplate(self.buffer, pagesize=self.pagesize, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
        doc.build(story)


# --- Fonctions simplifiées qui appellent le générateur ---
def generate_invoice_pdf(invoice):
    buffer = BytesIO()
    generator = BasePDFGenerator(buffer, A4)
    generator.build_pdf(invoice, "FACTURE")
    pdf = buffer.getvalue()
    buffer.close()
    return pdf

def generate_quote_pdf(quote):
    buffer = BytesIO()
    generator = BasePDFGenerator(buffer, A4)
    generator.build_pdf(quote, "DEVIS")
    pdf = buffer.getvalue()
    buffer.close()
    return pdf

def generate_credit_note_pdf(credit_note):
    buffer = BytesIO()
    generator = BasePDFGenerator(buffer, A4)
    generator.build_pdf(credit_note, "NOTE DE CRÉDIT")
    pdf = buffer.getvalue()
    buffer.close()
    return pdf