import pandas as pd
import time
import csv
import qrcode
import textwrap

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image, Spacer, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm

def read_sheet():
	SHEET_ID = '1f7o1pda1xsHnE7BnWxwDMog0XcjnGnL-WyJZ8W2eRks'
	SHEET_NAME = 'ToDo'
	url = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}'
	df = pd.read_csv(url)
	df.to_csv('info_musica.csv', index=False, encoding='utf-8')

def create_list():
	with open('info_musica.csv', 'r') as f:
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


def create_qr(titol, artista, year, link):
	if all(len(lst) == len(titol) for lst in [titol, artista, year, link]):
		for i in range(len(titol)):
			qr = qrcode.QRCode(
			        version=1,
			        box_size=10,
			        border=5)
			qr.add_data(link[i])
			qr.make(fit=True)
			titol[i] = titol[i].replace("/", "").replace(" ", "")
			artista[i] = artista[i].replace("/", "").replace(" ", "")
			img = qr.make_image(fill='black', back_color='white')
			img.save(f'tracks/{titol[i]}_{artista[i]}_{year[i]}.png')
			#print(f'tracks/{titol[i]}_{artista[i]}_{year[i]}.png')

def create_pdf_qr(titol, artista, year):
	# Create a PDF and add the QR code and text to it
	c = canvas.Canvas("./qr_list.pdf", pagesize=letter)
	x = 0.5
	y = 22.5
	offset_x = 0
	offset_y = 0
	row = 0
	for i in range(len(titol)):
		titol[i] = titol[i].replace("/", "").replace(" ", "")
		artista[i] = artista[i].replace("/", "").replace(" ", "")
		qr_img_path = f'tracks/{titol[i]}_{artista[i]}_{year[i]}.png'
		print(qr_img_path)
		c.drawImage(qr_img_path, (x+ offset_x) * cm, (y - offset_y) * cm,width= 5 * cm, height= 5 * cm)
		if (i+1)%4 != 0:
			offset_x += 5
		else:
			offset_x = 0
			offset_y += 4.5
			print("---------------------------------OFFSET " + str(offset_y)+"-----------------------------------------")
			row+=1
		if row == 6:
			offset_x = 0
			offset_y = 0
			row = 0
			c.showPage()
			print("---------------------------------NEW PAGE-----------------------------------------")
	c.save()

def create_pdf_info(titol, artista, year):
	# Create a PDF and add the QR code and text to it
	c = canvas.Canvas("./info_list.pdf", pagesize=letter)
	x = 1
	y = 26.5
	offset_x = 0
	offset_y = 0
	row = 0
	max_width = 15
	for i in range(len(titol)):
		qr_img_path = f'tracks/{titol[i].replace("/", "").replace(" ", "")}_{artista[i].replace("/", "").replace(" ", "")}_{year[i]}.png'
		print(qr_img_path)
		if len(titol[i]) > max_width:
			wrap_text = textwrap.wrap(titol[i], width=max_width)
			for j in range(len(wrap_text)):
				c.drawString((x + offset_x - 0.25) * cm, (y - offset_y - j * 0.37) * cm, wrap_text[j])
		else:
			c.drawString((x + offset_x) * cm, (y - offset_y) * cm, titol[i])
		c.drawString((x + offset_x + 0.5) * cm, (y - offset_y - 1.15) * cm, year[i])
		if len(artista[i]) > max_width:
			wrap_text = textwrap.wrap(artista[i], width=max_width)
			for j in range(len(wrap_text)):
				c.drawString((x + offset_x) * cm, (y - offset_y - j * 0.35 - 1.75) * cm, wrap_text[j])
		else:
			c.drawString((x + offset_x) * cm, (y - offset_y - 1.75) * cm, artista[i])
		if (i+1)%4 != 0:
			offset_x += 5
		else:
			offset_x = 0
			offset_y += 4.5
			print("---------------------------------OFFSET " + str(offset_y)+"-----------------------------------------")
			row+=1
		if row == 6:
			offset_x = 0
			offset_y = 0
			row = 0
			c.showPage()
			print("---------------------------------NEW PAGE-----------------------------------------")
	c.save()


if __name__ == '__main__':
	read_sheet()
	titol, artista, year, link = create_list()
	create_qr(titol, artista, year, link)
	create_pdf_qr(titol, artista, year)
	create_pdf_info(titol, artista, year)