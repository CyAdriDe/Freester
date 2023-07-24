import pandas as pd
import time
import csv
import qrcode

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image, Spacer, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

def read_sheet():
	SHEET_ID = '1f7o1pda1xsHnE7BnWxwDMog0XcjnGnL-WyJZ8W2eRks'
	SHEET_NAME = 'ToDo'
	url = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}'
	df = pd.read_csv(url)
	df.to_csv('info_musica.csv', index=False, encoding='utf-8')

def create_list():
	TEMPS_ESPERA = 3 # Temps d'espera entre frases
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

	titol.pop(0) # Eliminem el títol de la columna
	artista.pop(0)
	year.pop(0)
	link.pop(0)

	return titol, artista, year, link


def create_qr(titol, artista, year, link):
	if all(len(lst) == len(titol) for lst in [titol, artista, year, link]):
		for i in range(len(titol) - 1):
			qr = qrcode.QRCode(
			        version=1,
			        box_size=10,
			        border=5)
			qr.add_data(link[i])
			qr.make(fit=True)
			file_name = titol[i].replace("/", "")
			img = qr.make_image(fill='black', back_color='white')
			img.save(f'tracks/{file_name}_{artista[i]}_{year[i]}.png')

def create_pdf(titol, artista, year, link):
	pass

if __name__ == '__main__':
	read_sheet()
	titol, artista, year, link = create_list()
	create_qr(titol, artista, year, link)