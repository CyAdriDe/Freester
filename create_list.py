import pandas as pd
import datetime
import csv
import requests
import os
from dotenv import load_dotenv
import xml.etree.ElementTree as ET
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

def get_token():
	url = 'https://accounts.spotify.com/api/token'
	payload = {
	    'grant_type': 'client_credentials',
	    'client_id': os.getenv('CLIENT_ID'),
	    'client_secret': os.getenv('CLIENT_SECRET')
	}
	headers = {
	    'Content-Type': 'application/x-www-form-urlencoded'
	}
	response = requests.post(url, data=payload, headers=headers)

	return response.json()['access_token']

def get_playlist(token):
	playlist_length = 750
	offset = 0
	limit = 50
	list_ids = []
	playlist_id = os.getenv('PLAYLIST_ID')
	while playlist_length > offset:
		url = 'https://api.spotify.com/v1/playlists/'+playlist_id+'/tracks?fields=items%28track%28id%29%29&limit='+str(limit)+'&offset='+str(offset)
		headers = {
		    'Authorization': 'Bearer ' + token
		}
		response = requests.get(url, headers=headers)
		tracks = response.json()['items']
		for i in tracks:
			#print(i['track']['id'])
			list_ids.append(i['track']['id'])
		offset += 50

	return list_ids

def get_info(token, list_ids):
	headers = {
	    'Authorization': 'Bearer ' + token
	}
	#Borrem l'arxiu anterior
	with open('songs_spoty.csv', 'w', newline='') as file:
			writer = csv.writer(file)
			fields = ['Titulo','Artista','Año','URL']
			writer.writerow(fields)
			file.close()
	for track_id in list_ids:
		url = 'https://api.spotify.com/v1/tracks/'+ track_id
		response = requests.get(url, headers=headers)
		response = response.json()
		year_song = search_year_song(response['name'], response['artists'][0]['name'])
		if year_song == None:
			year_song = response['album']['release_date'][0:4]
		elif int(year_song) > int(response['album']['release_date'][0:4]):
			year_song = response['album']['release_date'][0:4]
		info = [response['name'], response['artists'][0]['name'], str(year_song), response['external_urls']['spotify']]
		print(info)
		with open('songs_spoty.csv', 'a', newline='') as file:
			writer = csv.writer(file)
			writer.writerow(info)
			print("---")
			file.close()

def search_year_song(titulo, artista):
	# Formato de la URL para la búsqueda (en este caso, en formato XML)
	print("Searching for " + titulo + " by " + artista)
	url = f"https://musicbrainz.org/ws/2/release?query=recording:{titulo} AND artist:{artista}&fmt=json"

	respuesta = requests.get(url)
	if respuesta.status_code != 200:
		print("Code error in response")
		return None

	# Analizar la respuesta
	data = respuesta.json()
	oldest_date = datetime.date.today().year + 1
	try:
		for recording in data['releases']:
			if 'title' in recording and recording['title'].strip().lower() == titulo.strip().lower():
				last_date = recording['date'][0:4]
				if last_date == '':
					continue
				last_date = int(last_date)
				if oldest_date > last_date:
					oldest_date = last_date
			else:
				print("Comparation failed!!!")
				break
	except:
		print("Problem, passing...")

	if oldest_date >= datetime.date.today().year:
		return None
	else:
		return oldest_date


def update_songs():
	load_dotenv()
	token = get_token()
	list_ids = get_playlist(token)
	get_info(token, list_ids)