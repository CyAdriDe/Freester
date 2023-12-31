import pandas as pd
import csv
import qrcode
import textwrap
import PyPDF2

import datetime
import requests
import os
from dotenv import load_dotenv
import xml.etree.ElementTree as ET
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image, Spacer, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from create_list import update_songs

def read_sheet():
	SHEET_ID = '1f7o1pda1xsHnE7BnWxwDMog0XcjnGnL-WyJZ8W2eRks'
	SHEET_NAME = 'ToDo'
	url = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}'
	df = pd.read_csv(url)
	df.to_csv('info_musica.csv', index=False, encoding='utf-8')

def create_list(csv_name):
	with open(csv_name, 'r') as f:
		titol = []
		artista = []
		year = []
		link = []
		reader = csv.reader(f, delimiter = ",")
		for row in reader:
			titol.append(row[0])
			artista.append(row[1])
			year.append(row[2])
			link.append(row[3])

	# Eliminem el títol de la columna
	titol.pop(0)
	artista.pop(0)
	year.pop(0)
	link.pop(0)

	return titol, artista, year, link

def compare_lists(link, titol_spoty, artista_spoty, year_spoty, link_spoty):
	
	diff_links = list(set(link) ^ set(link_spoty))

	with open('new_songs.csv', 'w', newline='') as file:
			writer = csv.writer(file)
			fields = ['Titulo','Artista','Año','URL']
			writer.writerow(fields)
			file.close()
	for i in range(len(titol_spoty)):
		if link_spoty[i] in diff_links:
			with open('new_songs.csv', 'a', newline='') as file:
				writer = csv.writer(file)
				fields = [titol_spoty[i],artista_spoty[i],year_spoty[i],link_spoty[i]]
				writer.writerow(fields)
				file.close()

def create_qr(titol, artista, year, link):
	if all(len(lst) == len(titol) for lst in [titol, artista, year, link]):
		for i in range(len(titol)):
			qr = qrcode.QRCode(
			        version=1,
			        box_size=10,
			        border=5)
			qr.add_data(link[i])
			qr.make(fit=True)
			titol_qr = titol[i].replace("/", "").replace(" ", "")
			artista_qr = artista[i].replace("/", "").replace(" ", "")
			img = qr.make_image(fill='black', back_color='white')
			img.save(f'tracks/{titol_qr}_{artista_qr}_{year[i]}.png')
			#print(f'tracks/{titol[i]}_{artista[i]}_{year[i]}.png')

def create_pdf_qr(titol, artista, year):
	# Create a PDF and add the QR code and text to it
	c = canvas.Canvas("./qr_list.pdf", pagesize=letter)
	num_por_fila = 4
	espacio_qr = 5  # Espacio para cada QR (en cm)
	espacio_linea = 0.4  # Espacio para las líneas (en cm)
	ancho_pagina, alto_pagina = letter

	# Calcular la posición inicial (superior derecha)
	x_inicial = ancho_pagina / cm - espacio_qr
	y = alto_pagina / cm - espacio_qr

	for i in range(len(titol)):
		titol_qr = titol[i].replace("/", "").replace(" ", "")
		artista_qr = artista[i].replace("/", "").replace(" ", "")
		qr_img_path = f'tracks/{titol_qr}_{artista_qr}_{year[i]}.png'

		# Dibujar el QR
		c.drawImage(qr_img_path, x_inicial * cm, y * cm, width=espacio_qr * cm, height=espacio_qr * cm)

		# Dibujar línea vertical después del QR, si no es el último de la fila
		if (i + 1) % num_por_fila != 0:
			c.line((x_inicial - espacio_linea) * cm, (y + espacio_qr) * cm, (x_inicial - espacio_linea) * cm, y * cm)

		# Actualizar la posición x
		x_inicial -= espacio_qr + espacio_linea
		if (i + 1) % num_por_fila == 0:
			# Dibujar línea horizontal debajo de la fila
			c.line(0, y * cm, ancho_pagina, y * cm)

			# Reiniciar x y actualizar y para la siguiente fila
			x_inicial = ancho_pagina / cm - espacio_qr
			y -= espacio_qr + espacio_linea

			# Verificar si se necesita una nueva página
			if y < espacio_qr:
				c.showPage()
				y = alto_pagina / cm - espacio_qr

	c.save()

def create_pdf_info(titol, artista, year):
    c = canvas.Canvas("./info_list.pdf", pagesize=letter)
    num_por_fila = 4
    espacio_qr = 5  # Espacio para cada recuadro (en cm)
    espacio_linea = 0.4  # Espacio para las líneas (en cm)
    ancho_pagina, alto_pagina = letter

    x_inicial = espacio_linea
    y = alto_pagina / cm - espacio_qr - espacio_linea

    max_width = 20  # Ancho máximo para el texto antes de envolver

    for i in range(len(titol)):
        # Posicionamiento del texto dentro del recuadro
        offset_texto = 0.5  # Ajuste vertical para el texto dentro del recuadro
        y_texto = y + espacio_qr - offset_texto

        # Dibujo del título
        wrap_text = textwrap.wrap(titol[i], width=max_width)
        for j, line in enumerate(wrap_text):
            text_width = c.stringWidth(line, 'Helvetica', 12)
            c.drawString((x_inicial + (espacio_qr - text_width / cm) / 2) * cm, (y_texto - j * 0.5) * cm, line)

        # Cambio de estilo para el año
        c.setFont("Helvetica-Bold", 14)
        text_width = c.stringWidth(year[i], 'Helvetica-Bold', 16)
        c.drawString((x_inicial + (espacio_qr - text_width / cm) / 2) * cm, (y_texto - len(wrap_text) * 0.5 - 1) * cm, year[i])

        # Cambio de estilo para el artista
        c.setFont("Helvetica", 12)
        wrap_text = textwrap.wrap(artista[i], width=max_width)
        for j, line in enumerate(wrap_text):
            text_width = c.stringWidth(line, 'Helvetica', 12)
            c.drawString((x_inicial + (espacio_qr - text_width / cm) / 2) * cm, (y_texto - len(wrap_text) * 0.5 - 2.65 - j * 0.5) * cm, line)

        # Dibujo de línea vertical después del recuadro, si no es el último de la fila
        if (i + 1) % num_por_fila != 0:
            c.line((x_inicial + espacio_qr) * cm, y * cm, (x_inicial + espacio_qr) * cm, (y + espacio_qr) * cm)

        # Actualizar la posición x
        x_inicial += espacio_qr + espacio_linea
        if (i + 1) % num_por_fila == 0:
            # Dibujo de línea horizontal debajo de la fila
            c.line(0, y * cm, ancho_pagina, y * cm)

            # Reiniciar x y actualizar y para la siguiente fila
            x_inicial = espacio_linea
            y -= espacio_qr + espacio_linea

            # Verificar si se necesita una nueva página
            if y < espacio_qr:
                c.showPage()
                y = alto_pagina / cm - espacio_qr - espacio_linea

    c.save()

def alternar_pdfs(pdf_info, pdf_qr, pdf_salida):
    pdf_info_reader = PyPDF2.PdfReader(pdf_info)
    pdf_qr_reader = PyPDF2.PdfReader(pdf_qr)
    pdf_writer = PyPDF2.PdfWriter()

    # Obtener el número máximo de páginas
    num_pags_info = len(pdf_info_reader.pages)
    num_pags_qr = len(pdf_qr_reader.pages)
    num_pags_max = max(num_pags_info, num_pags_qr)

    for i in range(num_pags_max):
        if i < num_pags_info:
            pdf_writer.add_page(pdf_info_reader.pages[i])
        if i < num_pags_qr:
            pdf_writer.add_page(pdf_qr_reader.pages[i])

    with open(pdf_salida, 'wb') as out_file:
        pdf_writer.write(out_file)

if __name__ == '__main__':
	#update_songs()
	#read_sheet()
	titol, artista, year, link = create_list('info_musica.csv')
	#titol_spoty, artista_spoty, year_spoty, link_spoty = create_list('songs_spoty.csv')
	#compare_lists(link, titol_spoty, artista_spoty, year_spoty, link_spoty)
	#create_qr(titol, artista, year, link)
	create_pdf_qr(titol, artista, year)
	create_pdf_info(titol, artista, year)
	alternar_pdfs("info_list.pdf", "qr_list.pdf", "freester.pdf")