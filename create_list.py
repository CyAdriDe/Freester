import pandas as pd
import time
import csv
import requests
import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

def create_list():
	with open('tracks.csv', 'r') as f:
		musica = []
		reader = csv.reader(f, delimiter = ",")
		for row in reader:
			musica.append(row)
	musica = musica[::-1]
	musica.pop() # Eliminem el títol de la columna
	
	return musica

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
	playlist_length = 748
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
			print(i['track']['id'])
			list_ids.append(i['track']['id'])
		offset += 50

	return list_ids

def get_info(token, list_ids):
	headers = {
	    'Authorization': 'Bearer ' + token
	}
	#Borrem l'arxiu anterior
	with open('songs.csv', 'w', newline='') as file:
			writer = csv.writer(file)
			fields = ['Titulo','Artista','Año','URL']
			writer.writerow(fields)
			file.close()
	for track_id in list_ids:
		url = 'https://api.spotify.com/v1/tracks/'+ track_id
		response = requests.get(url, headers=headers)
		response = response.json()
		info = [response['name'], response['artists'][0]['name'], response['album']['release_date'][0:4], response['external_urls']['spotify']]
		with open('songs.csv', 'a', newline='') as file:
			writer = csv.writer(file)
			writer.writerow(info)
			file.close()


if __name__ == '__main__':
	load_dotenv()
	token = get_token()
	list_ids = get_playlist(token)
	get_info(token, list_ids)
