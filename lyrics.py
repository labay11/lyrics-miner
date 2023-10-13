from nltk.corpus import stopwords
from nltk.stem.snowball import SpanishStemmer
from nltk.stem import WordNetLemmatizer
from nltk.stem.arlstem import ARLSTem
from urllib.request import urlopen
from bs4 import BeautifulSoup
import string
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import os
import time

BASE_URL = 'https://www.letras.com'

CODE_PLATERO = 'platero-y-tu' # 16157
CODE_FITO = 'fito-fitipaldis' # 5850
CODE_EXTREMO = 'extremoduro' # 5663
CODE_ROBE = 'robe-iniesta' # 36260
CODE_TAYLOR = 'taylor-swift'

STOPWORDS = stopwords.words('english')

print(STOPWORDS)

def artist_url(artist_code):
	return BASE_URL + f'/{artist_code}/mais_acessadas.html'
	# return BASE_URL + f'letras.asp?letras={artist_code}&orden=alf'

def find_artist_songs(artist_code):
	# musica.com -> listado-letras
	# metras.com -> cnt-list-songs
	with urlopen(artist_url(artist_code)) as web:
		html = BeautifulSoup(web, 'html.parser')
		songs = html.find('ul', 'songList-table-content')
		for link in songs.find_all('a', 'songList-table-songName'):
			yield (BASE_URL + link['href'])
			time.sleep(0.5)

def process_lyrics(text, 
	remove_duplicates=True,
	stopwords=None,
	lemm=None):
	words = text.split(' ')
	if stopwords:
		words = filter(lambda w: w not in stopwords, words)
	if lemm:
		words = map(lemm.lemmatize, words)
	if remove_duplicates:
		words = list(set(words))
	return ' '.join(words)

def lyrics(url):
	print(url)
	with urlopen(url) as web:
		html = BeautifulSoup(web, 'html.parser')
		
	lyrics = html.find('div', 'lyric-original')
	text = ' '.join([' '.join(verse.strings) for verse in lyrics.find_all('p')])
		
	# normalise lyrics
	text = text.lower().strip()
	text = text.translate(str.maketrans("","", string.punctuation + string.digits + '¡¿'))
	return text

def generate_wordcloud(artist_code):
	artist_file = f'{artist_code}.txt'
	if not os.path.exists(artist_file):
		all_songs = [lyrics(song) for song in find_artist_songs(artist_code)]
		with open(artist_file, 'w') as outf:
			outf.write('\n'.join(all_songs))
	
	stem = ARLSTem()
	with open(artist_file, 'r') as inf:
		all_songs = inf.read()
	all_songs = ' '.join([process_lyrics(song, lemm=WordNetLemmatizer(), stopwords=STOPWORDS) for song in all_songs.split('\n')])

	wc = WordCloud(width=800, height=600, stopwords=STOPWORDS).generate(all_songs)
	wc.to_file(f'{artist_code}.png')
	plt.imshow(wc, interpolation='bilinear')
	plt.axis("off")
	plt.show()

# generate_wordcloud('estopa')
# generate_wordcloud('marea')
# generate_wordcloud('mago-de-oz-musicas')
generate_wordcloud(CODE_TAYLOR)
