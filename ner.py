
import csv
from bs4 import BeautifulSoup as bs
import urlparse
from urllib2 import urlopen
from urllib import urlretrieve
import os
import sys
import wikipedia
import re
from nltk.corpus import stopwords
from nltk.tag import StanfordNERTagger
import nltk
from nltk.stem.snowball import SnowballStemmer
from collections import defaultdict
from nltk.corpus import wordnet as wn
from geograpy import places

# Loading the Wordnet domains.
domain2synsets = defaultdict(list)
synset2domains = defaultdict(list)


def count_upper(tag):
	k=0
	for s in tag:
		if s.isupper():
			k+=1
	return k

def process_split_text(text):
	for i in range(len(text)):
		if i>0 and i<len(text)-1:
			if text[i].lower()=='international' or text[i].lower()=='technologies' or text[i].lower()=='systems' or text[i].lower()=='solutions':
				text[i]=text[i-1]+text[i]
			if text[i].lower()=='united':
				text[i]=text[i]+text[i+1]
	return text


def process_dico_keys(dico):
	for key in dico.keys():
		split_key=key.lower().replace(',','').split(' ')
		l=['international','technologies', 'systems','solutions' ]
		if 'international' in split_key or 'technologies' in split_key or 'systems' in split_key or 'solutions' in split_key:
			for elt in l:
				try:
					index=split_key.index(elt)
					dico[split_key[index-1].lower()+split_key[index].lower()]=dico.pop(key)
				except ValueError:
					pass
				except KeyError:
					pass
		if 'united' in split_key:
			dico['united'+split_key[split_key.index('united')+1].lower()]=dico.pop(key)



stop = stopwords.words('english')
stop.append('around')
stop.append('top')
stop.append('new')
stop.append('else')
stop.append('next')

stemmer = SnowballStemmer("english")

with open('/Users/victorstorchan/Desktop/namelist.csv', mode='rU') as infile:
	reader = csv.reader(infile, dialect=csv.excel_tab)
	dict_name=dict((rows[0],'name') for rows in reader)

with open('/Users/victorstorchan/Desktop/lastname.csv', mode='rU') as infile:
	reader = csv.reader(infile, dialect=csv.excel_tab)
	dict_lastname=dict((rows[0],'name') for rows in reader)

with open('/Users/victorstorchan/Desktop/top100apps.csv', mode='rU') as infile:
	reader = csv.reader(infile, dialect=csv.excel_tab)
	dict_apps=dict((rows[0].split(',')[1],'name') for rows in reader)


with open('/Users/victorstorchan/Desktop/companylist.csv', mode='r') as infile:
	reader = csv.reader(infile)
	dict_1m = dict((rows[1],rows[0]) for rows in reader)
	dict_1m['Google']='Google'
	dict_1m['Amazon']='Amazon'
	dict_1m['IBM']='IBM'



process_dico_keys(dict_1m)
for key in dict_1m.keys():
	list_from_key= key.split()
	if len(list_from_key)==1:
		dict_1m[list_from_key[0].replace(',','').lower()]=dict_1m.pop(key)
	if len(list_from_key)>=2:
		if count_upper(list_from_key[0])>=2:
			dict_1m[list_from_key[0].replace(',','').lower()]=dict_1m.pop(key)
		if list_from_key[0].lower()=='the' or  list_from_key[0].lower()=="top" or list_from_key[0].lower()=="new":
			dict_1m[list_from_key[1].replace(',','').lower()]=dict_1m.pop(key)
		else:
			try:
				dict_1m[list_from_key[0].replace(',','').lower()]=dict_1m.pop(key)
			except KeyError:
				pass




symlist=[ 'company','corporation','multinational', 'Corporation','open-source','social', 'network','software','system']
badlist=['ca','login','sitemap','follow''integrated','web','solution','services','limited','tech','solutions','technology','open','model','on','applied','network','comment', 'pricing','customers','social','big','subscribe','social','sign','monitor','software','machine','learning','compute','management','tech','up','Recruiting']
badlist_stem=[]
for i in range(len(badlist)):
	badlist_stem.append(stemmer.stem(badlist[i]))





for key in dict_1m.keys():
		if key[len(key)-4:len(key)]=='.com':
			dict_1m[key[0:len(key)-4]]='added'


dead=dict_1m.pop("new", None)
dead=dict_1m.pop("top", None)
dead=dict_1m.pop("on", None)
dead=dict_1m.pop("model", None)
dead=dict_1m.pop("energy", None)
dead=dict_1m.pop("silicon", None)
dead=dict_1m.pop("innovative", None)
dead=dict_1m.pop("digital", None)
dead=dict_1m.pop("tech", None)
dead=dict_1m.pop("team", None)
dead=dict_1m.pop("web", None)
dead=dict_1m.pop("ca", None)

st = StanfordNERTagger("/Users/victorstorchan/Downloads/stanford-ner-2014-06-16/classifiers/english.all.3class.distsim.crf.ser.gz",\
	"/Users/victorstorchan/Downloads/stanford-ner-2014-06-16/stanford-ner.jar")



def TechComp(url_):
	url=url_
	soup = bs(urlopen(url))
	parsed = list(urlparse.urlparse(url))
	contents= soup.find_all('a')
	content_text=soup.get_text().split()
	regex = re.compile('[^a-zA-Z]')
	stop = stopwords.words('english')
	clean_text=''
	for elt in content_text:
		if  regex.sub('', elt) !='' and regex.sub('', elt) not in stop:
			clean_text+= ' '+regex.sub('', elt)
	clean_text_split=clean_text.split()
	clean_text_split=process_split_text(clean_text_split)
	paragraphs = []
	paragraphs_string=''
	for x in clean_text_split:
		paragraphs.append(str(x))
	paragraphs_string=' '.join(paragraphs)
	tagging=st.tag(paragraphs_string.split())
	pretag1= [tag for (tag,label) in tagging if label in set(("ORGANIZATION","PERSON")) or (count_upper(tag)>=2 and len(tag)<11 ) ]
	pretag2=[tag for (tag,label) in tagging if tag.lower() in dict_1m or tag in dict_apps]
	pretag= pretag1+pretag2
	l=[]
	for tag in pretag:
		if tag.lower() in dict_1m or tag in dict_apps:
			l.append(tag)
		else:
			if len(tag)<20 and len(tag)>1 and wn.synsets(tag,pos=wn.NOUN)==[] and stemmer.stem(tag) not in badlist_stem and tag not in dict_name and tag not in dict_lastname and tag.lower() not in stop:
				l.append(tag)
	pc=places.PlaceContext(l)
	pc.set_countries()
	countries=pc.countries
	pc.set_regions()
	regions=pc.regions
	pc.set_cities()
	cities=pc.cities
	location=cities+countries+regions
	l2 = [elt for elt in l if elt not in location]
	l3=[elt for elt in l2 if wn.synsets(elt,pos=wn.ADJ)==[]]
	return l3
