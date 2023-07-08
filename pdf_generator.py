from reportlab.lib.units import cm
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.graphics.barcode import createBarcodeDrawing
from reportlab.graphics.shapes import Drawing
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY
from ticketboss import utils
from ticketboss.models.tickets import Discount
import logging
from .base import BaseTicketGenerator

logger = logging.getLogger(__name__)


class TicketGresca2023Generator(BaseTicketGenerator):
    def __init__(self):
        super(TicketGresca2023Generator, self).__init__()
        self.condicions = [
            ("Identificació Promotora: ",
             "Associació Cultural TGK (d'ara en endavant l’“Organització”). Domicili social a Barcelona (08034) "
             "Carrer Jordi Girona número 1-3, Edifici Omega, Despatx 106. N.I.F G-65.748.394. Inscrita degudament "
             "en el Registre d'Associacions de la Generalitat de Catalunya amb nombre d'inscripció 47.028."),
            ("Adquisició d'entrades i accés al recinte: ",
             "L'Organització no garanteix l’autenticitat de l’entrada si no ha estat adquirida en un punt de venda "
             "oficial. Les entrades són personals i intransferibles. L'entrada dóna dret al seu portador a accedir "
             "al recinte una sola vegada."),
            ("Dret d'admissió: ",
             "No es permetrà l'accés al recinte a aquelles persones que manifestin actituds violentes o que incitin "
             "públicament a l'odi, la violència o la discriminació. No es permetrà l'accés al recinte a aquelles "
             "persones que es comportin de forma agressiva o provoquin altercats a l'exterior del recinte o a "
             "l'entrada ni a aquelles persones que portin armes, artificis pirotècnics o objectes susceptibles "
             "de ser utilitzats com a tals. No es permetrà l'accés al recinte a les persones que mostrin símptomes "
             "d'embriaguesa o que estiguin consumint drogues o substàncies estupefaents o mostrin símptomes "
             "d'haver-les consumit."),
            ("",
             "Per a més informació de les presents condicions pot consultar-les a la web "
             "www.telecogresca.com/media/docs/condicionsGresca.pdf")
        ]
        self.footer = 'Associació Cultural TGK | Carrer Jordi Girona, 1-3 Edifici Omega Despatx 106 Campus Nord' \
                      ' UPC 08034 Barcelona | NIF: G65748394 | Tel: 934 137 662'
        self.extra_info = "El sistema d'entrades no admetrà més d'una còpia de l'entrada, només la primera serà " \
                          "acceptada. Per a més seguretat l'organització es reserva el dret a sol.licitar el DNI " \
                          "per accedir al recinte."

        # Styles
        self.stylesheet = getSampleStyleSheet()
        self.stylesheet.add(
            ParagraphStyle(name='CondicionsStyle', fontName='Helvetica', fontSize=7, leading=9.5, alignment=TA_JUSTIFY))
        self.condicionsstyle = self.stylesheet['CondicionsStyle']

    def generate_page(self, canvas, ticket):
        # Banner i part superior
        code = ticket.type.letter + ticket.token

        code = code + utils.generate_barcode_checksum(code)

        logger.debug("Generant ticket pel paco %s", ticket.name)
        logger.debug("extra_data:")
        logger.debug(ticket.type.extra_pdf_data)
        type_image = ticket.type.extra_pdf_data['image']
        promo_image = ticket.type.extra_pdf_data['image_promo']
        canvas.drawImage(self.images[type_image],
                         0 * cm, self.pageheight - 9 * cm, width=21 * cm, height=9 * cm)
        canvas.drawImage(self.images[promo_image],
                         0 * cm, self.pageheight - 15.3 * cm, width=21 * cm, height=6 * cm)
        canvas.line(1 * cm, self.pageheight - 17.2 * cm, 20 * cm, self.pageheight - 17.2 * cm)
        canvas.setFont("Helvetica", 30)
        canvas.drawString(1.11 * cm, self.pageheight - 16.85 * cm, ticket.type.name)

        # load group of tickets
        group = ticket.group

        # Dades de l'entrada
        info_text = [
            ['Nom complet: ', ticket.get_full_name()],
            ['Tipus: ', ticket.type.description],
        ]

        if hasattr(group, 'payment'):
            # has a payment and therefore, a price
            price_to_display = ticket.type.price
            if ticket.discounted:
                applied_discount = Discount.objects.filter(name = ticket.extra_data.get('applied_discount')).last()
                price_to_display -= ticket.type.fee
                price_to_display *= (1 - applied_discount.discount)
                price_to_display += ticket.type.fee
            price = '{:2,.2f}€'.format(price_to_display)
            price += ' (despeses de gestió {:2,.2f}€)'.format(ticket.type.fee)
            info_text.append(['Preu: ', price, ])
            if ticket.discounted:
                info_text.append(['', applied_discount.description])

        info_text.append(['Codi de seguretat: ', "%s" % utils.generate_security_code(ticket.id)])

        for index, (key, value) in enumerate(info_text):
            canvas.setFont("Helvetica", 12)
            canvas.drawString(1.11 * cm, self.pageheight - (18.5 + 0.5 * (index - 1)) * cm, key)
            canvas.setFont("Helvetica-Bold", 12)
            jump = stringWidth(key, 'Helvetica', 12)
            canvas.drawString(1.11 * cm + jump, self.pageheight - (18.5 + 0.5 * (index - 1)) * cm, value)

        # LLetraca i logo
        canvas.setFont("Helvetica", 150)
        canvas.drawString(10.6 * cm, self.pageheight - 22.75 * cm, ticket.type.letter)
        canvas.drawImage(self.images['logo_gresca'], 15 * cm, self.pageheight - 22.75 * cm, width=3 * cm, height=3 * cm)

        # Condicions extres
        p = Paragraph(self.extra_info, self.condicionsstyle)
        p.wrapOn(canvas, 6 * cm, self.pageheight)
        p.drawOn(canvas, 12.31 * cm, self.pageheight - 18.65 * cm)

        # Barcodes
        barcode_QR = createBarcodeDrawing('QR', value=code, barWidth=6.5 * cm, barHeight=6.5 * cm)
        barcode_QR.drawOn(canvas, 14.25 * cm, self.pageheight - 6.8 * cm)

        barcode_hor = createBarcodeDrawing('Code128', value=code, barWidth=(float(10) / (len(code) * 16)) * cm,
                                           barHeight=3 * cm)
        barcode_hor.drawOn(canvas, 0.4 * cm, self.pageheight - 23.25 * cm)
        # Vertical. S'ha de posar en un drawing per poder-lo girar.
        barcode_ver = createBarcodeDrawing('Code128', value=code, barWidth=(float(8) / (len(code) * 16)) * cm,
                                           barHeight=1 * cm)
        drawing = Drawing(8, 1)
        drawing.rotate(90)
        drawing.add(barcode_ver, name='barcode')
        drawing.drawOn(canvas, 20 * cm, self.pageheight - 28.2 * cm)

        # Condicions legals i barres vàries

        canvas.line(1 * cm, self.pageheight - 23.5 * cm, 18.5 * cm, self.pageheight - 23.5 * cm)
        condicionsText = ''
        for item, condicio in self.condicions:
            condicionsText += '- <strong>%s</strong>%s<br/>' % (item, condicio)
        p = Paragraph(condicionsText, self.condicionsstyle)
        p.wrapOn(canvas, 17.05 * cm, self.pageheight)
        p.drawOn(canvas, 1.09 * cm, self.pageheight - 27.3 * cm)
        canvas.line(1 * cm, self.pageheight - 27.4 * cm, 18.5 * cm, self.pageheight - 27.4 * cm)
        canvas.setFont("Helvetica", 7)
        canvas.drawString(1.07 * cm, self.pageheight - 27.7 * cm, self.footer)
