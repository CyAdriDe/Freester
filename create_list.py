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
	df.to_csv('tracks.csv', index=False, encoding='utf-8')

def create_list():
	with open('tracks.csv', 'r') as f:
		musica = []
		reader = csv.reader(f, delimiter = ",")
		for row in reader:
			musica.append(row)
	musica = musica[::-1]
	musica.pop() # Eliminem el títol de la columna
	
	return musica

def create_qr(musica):
    for item in musica:
	    qr = qrcode.QRCode(
	            version=1,
	            box_size=10,
	            border=5)
	    qr.add_data(item[3])
	    qr.make(fit=True)
	    img = qr.make_image(fill='black', back_color='white')
	    img.save(f'tracks/{item[0]}.png')

if __name__ == '__main__':
	read_sheet()
	musica = create_list()
	create_qr(musica)
