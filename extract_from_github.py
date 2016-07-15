rom base64 import b64decode
import requests
import json
import csv
from stdlib_list import stdlib_list
from nltk.corpus import gutenberg,reader
from nltk.tag.stanford import NERTagger
from difflib import SequenceMatcher

"""initialization: s=PythonRepo(url) where url is like https://github.com/scikit-learn/scikit-learn/blob/master/benchmarks/bench_glm.py
	then:
		1)s.get_python_file()
		2)s.remove_comments()
		3)-s.get_modules()
		    -s.get_packages()... etc

'"""

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()
dico_feature={}

with open('/Users/victorstorchan/Desktop/csv_files/list_tech_term.csv', mode='rU') as infile:
	reader = csv.reader(infile, dialect=csv.excel_tab)
	dict_tech=dict((rows[0],'name') for rows in reader)

def isupper_(word):
	k=0
	for i in word:
		if i.isupper() and k<2:
			k+=1
		if i.isupper() and k==2:
			return True
		else:
			pass
	return False

class PythonRepo:
	def __init__(self,url2):
		url_items=url2.split('/')[3:]
		url1='https://api.github.com/repos/'
		url1+=url_items[0]+'/'+url_items[1]+'/'+'contents'+'/'
		for elt in url_items[4:len(url_items)-1]:
			url1+=elt+'/'
		url1+=url_items[len(url_items)-1]+'?ref=master'
		self.url=url1	
	def  get_python_file(self):
		r = requests.get(self.url)
		repoItem = json.loads(r.text or r.content)
		text=b64decode(repoItem['content'])
		self.text=text.split('\n')
		return self.text
	def get_name_class(self):
		self.text=text
		list_class=[]
		for line in text:
			line1=line.split()
			if len(line1)>1:
				if line1[0].lower()=='class' :
					list_class.append(line1[1][0:line1[1].index('(')])
		return list_class
	def  get_list_stdli(self):
		return stdlib_list("2.7")
	def get_name_functions(self):
		self.text=text
		list_fun=[]
		for line in text:
			line1=line.split()
			if len(line1)>1:
				if line1[0]=='def':
					list_fun.append(line1[1][0:line1[1].index('(')])
		return list_fun
	def get_modules(self):
		text=self.text
		list_modules=[]
		for line in text:
			if 'import ' in line:
		 		list_=line.split()
				list_modules.append(list_[list_.index('import')+1])
				if '(' in list_[list_.index('import')+1]:
					for elt in list_[list_.index('import')+1:len(list_)]:
		 				if ')' not in elt:
		 					list_modules.append(elt)
						if ')' in elt and list_.index(elt)==len(list_)-1:
							list_modules.append(elt)
						if ')' not in elt and list_.index(elt)!=len(list_)-1:
							list_modules+=text[text.index(line)+1].split()
			for elt in list_modules:
				if ')' in elt:
					list_modules[list_modules.index(elt)]=elt.replace(')','')
				if '(' in elt:
					list_modules[list_modules.index(elt)]=elt.replace('(','')
				if ',' in elt:
					list_modules[list_modules.index(elt)]=elt.replace(',','')
			list_std=self.get_list_stdli()
			list_modules_bis=[]
			for elt in list_modules:
				if elt not in list_std:
					list_modules_bis.append(elt)
		self.list_modules_bis=list_modules_bis
		return self.list_modules_bis
	def remove_comments(self):
		text=self.text
		k=0
		new_text=[]
		for line in text:
			count_quote=line.count('"""')
			if count_quote==0 and   k==0:
				new_text.append(line)
			if count_quote==1 and k==0:
				k+=1
				line=line[0:line.index('"""')]
				new_text.append(line)
			elif count_quote==1 and k==1:
				k=0
				line=line[line.index('"""')+1:len(line)-2]
				new_text.append(line)
			elif count_quote==0 and k==1:
				pass
			elif count_quote ==2:
				line=line[0:line.index('"""')]+line[line.index('"""',1)+1:len(line)]
				new_text.append(line)
		final_text=[]
		for line in new_text:
			count_ashtag=line.count('#')
			if count_ashtag==1:
				line=line[0:line.index('#')]
				final_text.append(line)
			else:
				final_text.append(line)
		self.text=final_text
		return final_text
  	def get_renamed_modules(self):
  		text=self.text
  		list_modules=self.list_modules_bis
		dict_module_usedname={}
		for module in list_modules:
			dict_module_usedname[module]=module
			for line in text:
				list_=line.split()
				if 'import' in line and module in line and 'as' in list_:
					dict_module_usedname[module]=list_[list_.index('as')+1]
		return dict_module_usedname
	def get_packages(self):
		text=self.text
  		list_packages=[]
 		for line in text:
   			if 'from' in line:
     				list_=line.split()
      				list_packages.append(list_[list_.index('from')+1])
 		return   list_packages
 	def get_command(self):
 		text=self.text
		list_command=[]
		for line in text:
			list_=line.split()
			for elt in list_:
				if  '.' in elt:
					if '(' in elt :
						list_command.append(elt[0:elt.index('(')])
					elif '[' in elt:
						list_command.append(elt[0:elt.index('[')])
					elif ')' in elt:
						list_command.append(elt[0:elt.index(')')])
					elif ']' in elt:
						list_command.append(elt[0:elt.index(')')])
					else:
						list_command.append(elt)
		for elt in list_command:
			if '=' in elt:
				elt1=elt.replace(elt[0:elt.index('=')+1],'')
				list_command[list_command.index(elt)]=elt1
		list_unique_command=list(set(list_command))
		for elt in list_unique_command:
			if '.' not in elt:
				list_unique_command.remove(elt)
		for elt in list_unique_command:
			elt_split=elt.split('.')
			list_packages=self.get_packages()
			list_modules=self.get_modules()
			list_ren_modules=self.get_renamed_modules().values()
			if elt_split[0]  in list_packages  or elt_split[0]  in list_ren_modules:
				pass
			elif 'self' in elt_split:
				pass
			else:
				elt1=elt.replace(elt[0:len(elt_split[0])],'variable',1)
				list_unique_command[list_unique_command.index(elt)]=elt1
		return list_unique_command

#url2= 'https://github.com/scikit-learn/scikit-learn/blob/master/README.rst'
"""Note: if spec is specified, then the readme class can read other files than the read me. One has to specify 
the key word related to the file. E.G: to read the file from the following url: https://github.com/vhf/free-programming-books/blob/master/free-programming-books.md
one should pass spec = 'free-programming-books'    """
class readme:
	def __init__(self,url2,spec=''):
		url_items=url2.split('/')[3:]
		url1='https://api.github.com/repos/'
		url1+=url_items[0]+'/'+url_items[1]+'/'+'contents'
		r = requests.get(url1)
		repoItem = json.loads(r.text or r.content)
		for i in range(len(repoItem)):
			if 'README' in repoItem[i]['name'] and spec=='':
				url3=repoItem[i]['url']
			if spec!='' and spec in repoItem[i]['name']:
				url3=repoItem[i]['url']
		# for elt in url_items[4:len(url_items)-1]:
		# 	url1+=elt+'/'
		# if url_items[len(url_items)-1]=='README.rst':
		# 	url1+=url_items[len(url_items)-1]+'?ref=master'
		# if url_items[len(url_items)-1]=='README.md':
		# 	url1+=url_items[len(url_items)-1]+'?ref=develop'
		self.url=url3
	def  get_python_file(self):
		r = requests.get(self.url)
		repoItem = json.loads(r.text or r.content)
		text=b64decode(repoItem['content'])
		self.text=text.split('\n')
		return self.text
	def extract_meaningful_info(self):
		text=self.text
		text2=[]
		for line in text:
			text2+=line.split()
		words_spec=[]
		words_spec=[words for words in text2 if words not in list(set(gutenberg.words()[0:3000]))]
		tech_words=[words for words in text2 if words in dict_tech]
		link_from_readme=[elt.split('/')[2:] for elt in words_spec if 'https' in elt or 'http' in elt]
		link_from_readme=filter(lambda elt:elt!=[],link_from_readme)
		associated_website=[elt[0] for elt in link_from_readme if 'github' not in elt[0].lower()]
		associated_github=[elt[1]+'/'+elt[2] for elt in link_from_readme if 'github' in elt[0].lower()]
		self.words=words_spec
		self.links=link_from_readme
		self.associated_github=list(set(associated_github))
		self.associated_website=list(set(associated_website))
		self.tools=list(set([word for word in words_spec if isupper_(word) and 'http' not in word]))
		self.summarize=text2[0:50]
		self.technical=tech_words
		return words_spec
	def create_dico_of_features(self):
		dico_feature[self.url]={}
		dico_feature[self.url]['links']=self.links
		dico_feature[self.url]['associated_github']=self.associated_github
		dico_feature[self.url]['associated_website']=self.associated_website
		dico_feature[self.url]['technical']=self.technical
		dico_feature[self.url]['summarize']=self.summarize
		return dico_feature[self.url]




"""Figure out which extension to give on the __init__ function, to decide if it is develop or master with the lines:
r = requests.get('https://api.github.com/repos/scikit-learn/scikit-learn/contents')
repoItem = json.loads(r.text or r.content)
url=repoItem[len(repoItem)-1]['url'] 
r=requests.get(url)
"""

# s=readme('https://github.com/scikit-learn/scikit-learn/blob/master/README.rst')
# s.get_python_file()
# s.extract_meaningful_info()

