import json
import re
from nltk.corpus import stopwords
#from langdetect import detect
from unidecode import unidecode
from collections import Counter
import textacy
import numpy as np

"""langages equivalent+load the data in an rdd. One log per node"""
lang_from_detect_to_nltk={}
lang_from_detect_to_nltk['en']='english'
lang_from_detect_to_nltk['fr']='french'
lang_from_detect_to_nltk['fi']='finnish'
lang_from_detect_to_nltk['de']='german'
lang_from_detect_to_nltk['hu']='hungarian'
lang_from_detect_to_nltk['it']='italian'
lang_from_detect_to_nltk['no']='norwegian'
lang_from_detect_to_nltk['es']='spanish'
lang_from_detect_to_nltk['tr']='turkish'
lang_from_detect_to_nltk['pt']='portuguese'
lang_from_detect_to_nltk['da']='danish'


stop = stopwords.words('english')

path = "/Users/victorstorchan/Desktop/telepath_files/2016_06_15_html.log"
s=""
lines=open(path,'r')
for l in lines:
	s+=l
lines.close()
logs_str=s	
logs_list = [d.strip() for d in logs_str.splitlines()]
logs_json_html = [json.loads(i) for i in logs_list]

#one dictionary, ie one Eventtype per node:

logs_json_par= sc.parallelize(logs_json_html)
text= logs_json_par.map(lambda log: (log['data']['url'],unidecode(log['data']['content'])))
process1=text.map(lambda (a,b): (a,str(re.split("\W+| " "|\n|\t+",b)))).map(lambda (a,b):(a,b.lower())).filter(lambda (a,b): b!='')
process2=process1.map(lambda (a,b) :(a,re.sub('[^a-zA-Z0-9 \n\.]', '',b)))
process3=process2.map(lambda (a,b) :(a,re.sub('[[^0-9]*', '',b))).map(lambda (a,b):(a,b.split(" "))).map(lambda (a,b):(a,[ w for w in b if (w!="ut" and len(w[1:])>1 and w not in stop)]))
#process4=process3.map(lambda t: Counter(t).most_common(30))
process4=process3.map(lambda (a,b):(a,unicode(" ".join(str(x) for x in b))))
#process5=process4.map(lambda t: textacy.TextDoc(t.strip(), lang='en'))
#tokens_collect=process4.collect()
tokens_collect=process3.collect()

doc_from_textacy=[]
relevant_terms={}
shorten_token_collect=[]
for i in range(len(tokens_collect)):
	if len(tokens_collect[i][1])>20:
		shorten_token_collect.append(tokens_collect[i])

"""supprimer les tokens vides ou bien faire varier le n en fonction de la taille de la string
(meilleure idee) en supprimant le  cas n=0"""
for i in range(len(shorten_token_collect)):
	doc_from_textacy.append((shorten_token_collect[i][0],textacy.TextDoc(unicode(" ".join(str(x) for x in shorten_token_collect[i][1])).strip(), lang='en')))
for i in range(len(shorten_token_collect)):
	relevant_terms[doc_from_textacy[i][0]]=[doc_from_textacy[i][1].key_terms(algorithm='textrank', n=10),list(doc_from_textacy[i][1].named_entities(drop_determiners=True, bad_ne_types='numeric'))]


matrix_of_relation=np.zeros((len(shorten_token_collect),len(shorten_token_collect)))

def compute_len_intersection(l1,l2):
	return len([val for val in l1 if val in l2])

for i in range(len(shorten_token_collect)):
	for j in range(len(shorten_token_collect)):
		matrix_of_relation[i,j]= compute_len_intersection(relevant_terms[doc_from_textacy[i][0]][0],relevant_terms[doc_from_textacy[j][0]][0])+compute_len_intersection(relevant_terms[doc_from_textacy[i][0]][1],relevant_terms[doc_from_textacy[j][0]][1])





#process5_collect=process5.collect()
#for i in range(len(tokens_collect)):
	#logs_json_html[i]['data']['content']=tokens_collect[i]
	#logs_json_html[i]['lang']=lang_from_detect_to_nltk[detect(str(detect_lang_collect[i]))]


