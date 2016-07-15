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









def count_upper(tag):
	k=0
	for s in tag:
		if s.isupper():
			k+=1
	return k

stop = stopwords.words('english')
stop.append('around')
stop.append('top')
stop.append('new')
stop.append('else')
stop.append('next')

stemmer = SnowballStemmer("english")
with open('/Users/victorstorchan/Desktop/csv_files/list_tech_term.csv', mode='rU') as infile:
	reader = csv.reader(infile, dialect=csv.excel_tab)
	dict_tech=dict((rows[0].lower(),'name') for rows in reader)

with open('/Users/victorstorchan/Desktop/csv_files/namelist.csv', mode='rU') as infile:
	reader = csv.reader(infile, dialect=csv.excel_tab)
	dict_name=dict((rows[0],'name') for rows in reader)

with open('/Users/victorstorchan/Desktop/csv_files/lastname.csv', mode='rU') as infile:
	reader = csv.reader(infile, dialect=csv.excel_tab)
	dict_lastname=dict((rows[0],'name') for rows in reader)

with open('/Users/victorstorchan/Desktop/csv_files/top100apps.csv', mode='rU') as infile:
	reader = csv.reader(infile, dialect=csv.excel_tab)
	dict_apps=dict((rows[0].split(',')[1],'name') for rows in reader)


with open('/Users/victorstorchan/Desktop/csv_files/companylist.csv', mode='r') as infile:
	reader = csv.reader(infile)
	dict_1m = dict((rows[1],rows[0]) for rows in reader)
	dict_1m['Google']='Google'
	dict_1m['Amazon']='Amazon'
	dict_1m['IBM']='IBM'

'''Parse the keys of the dico dict_1m'''

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

dead=dict_1m.pop("new", None)
dead=dict_1m.pop("top", None)
dead=dict_1m.pop("on", None)

for key in dict_1m.keys():
		if key[len(key)-4:len(key)]=='.com':
			dict_1m[key[0:len(key)-4]]='added'

"""Process the bi gram keys of dict_1m"""

def process_dico_keys(key):
	split_key=key.lower().split(' ')
	l=['international','technologies', 'systems','solutions' ]
	if 'international' in split_key or 'technologies' in split_key or 'systems' in split_key or 'solutions' in split_key:
		for elt in l:
			try:
				index=split_key.index(elt)
				dict_1m[split_key[index-1].lower()+split_key[index].lower()]=dict_1m.pop(key)
			except ValueError:
				pass
	if 'united' in split_key:
		dict_1m['united'+split_key[split_key.index('united')+1].lower()]=dict_1m.pop(key)

for keys  in dict_1m.keys():
	process_dico_keys(key)



class ExtractNamedEntities:
	def __init__(self,url1):
		self.url=url1
		url=self.url
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
		self.text=clean_text_split

	def process_split_text(self):
		text=self.text
		for i in range(len(text)):
			if i>0 and i<len(text)-1:
				if text[i].lower()=='international' or text[i].lower()=='technologies' or text[i].lower()=='systems' or text[i].lower()=='solutions':
					text[i]=text[i-1]+text[i]
				if text[i].lower()=='united':
					text[i]=text[i]+text[i+1]
		return text
	def pretag(self):
		text=self.text
		st = StanfordNERTagger("/Users/victorstorchan/Downloads/stanford-ner-2014-06-16/classifiers/english.all.3class.distsim.crf.ser.gz",\
	"/Users/victorstorchan/Downloads/stanford-ner-2014-06-16/stanford-ner.jar")
		paragraphs = []
		paragraphs_string=''
		for x in text:
			paragraphs.append(str(x))
		paragraphs_string=' '.join(paragraphs)
		tagging=st.tag(paragraphs_string.split())
		symlist=[ 'company','corporation','multinational', 'Corporation','open-source','social', 'network','software','system']
		badlist=['integrated','first','check','computer','linear', 'solution','services','limited','tech','solutions','technology','open','model','on','applied','network', 'pricing','customers','social','big','subscribe','social','sign','monitor','software','machine','learning','compute','management','up']
		badlist_stem=[]
		self.badlist=badlist
		self.symlist=symlist
		for i in range(len(badlist)):
			badlist_stem.append(stemmer.stem(badlist[i]))
		self.badlist_stem=badlist_stem
		pretag1= [tag for (tag,label) in tagging if label in set(("ORGANIZATION","PERSON")) or (count_upper(tag)>=2 and len(tag)<11 ) ]
		pretag2=[tag for (tag,label) in tagging if tag.lower() in dict_1m or tag in dict_apps]
		pretag3=[tag for (tag,label) in tagging if tag.lower() in dict_tech]
		pretag= pretag1+pretag2+pretag3
		domain2synsets = defaultdict(list)
		synset2domains = defaultdict(list)
		self.pretag=pretag
		

	def find_tech_comp(self):
		pretag=self.pretag
		l=[]
		for tag in pretag:
			if tag.lower() in dict_1m or tag in dict_apps:
				if tag.lower() not in self. badlist:
					l.append(tag)
			if tag.lower() in dict_tech:
				l.append(tag)
			else:
				if wn.synsets(tag,pos=wn.NOUN)==[] and stemmer.stem(tag) not in self.badlist_stem and tag not in dict_name and tag not in dict_lastname and tag.lower() not in stop:
					l.append(tag)
		pc=places.PlaceContext(l)
		pc.set_countries()
		countries=pc.countries
		pc.set_regions()
		regions=pc.regions
		pc.set_cities()
		cities=pc.cities
		location=cities+countries+regions
		location2=[loc for loc in location if loc.lower() not in dict_tech ]
		self.location=location2
		l2 = [elt for elt in l if elt not in location2]
		self.entities=l2
		return l2




