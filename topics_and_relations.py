from nltk.corpus import gutenberg,reader
from nltk.stem.snowball import SnowballStemmer
import random
from nltk.tag import StanfordNERTagger
from operator import itemgetter
import wikipedia
from nltk.corpus import wordnet
from nltk.corpus import wordnet as wn
from collections import Counter





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


"""Get tokens from the raw text and label them with Epr, Pers, Acr"""

def get_tokens_topics(text):
	stemmer = SnowballStemmer("english")
	words_spec=[]
	words_spec=[words for words in text.split() if words not in gutenberg.words()[0:30000]]
	st = StanfordNERTagger("/Users/victorstorchan/Downloads/stanford-ner-2014-06-16/classifiers/english.all.3class.distsim.crf.ser.gz",\
	"/Users/victorstorchan/Downloads/stanford-ner-2014-06-16/stanford-ner.jar")
	tagged_words_spec=st.tag(words_spec)
	Person_tagged= [((person,"Pers"),tagged_words_spec.index((person,tag))) for (person,tag) in tagged_words_spec if tag=="PERSON" or tag=='ORGANIZATION']
	Acronym=[((words,"Acr"),tagged_words_spec.index((words,tag))) for (words,tag) in tagged_words_spec  if tag!="PERSON" and tag!= "LOCATION" and len(words) in range(2,6) and isupper_(words)  ]
	Expression=[((words+' '+tagged_words_spec[tagged_words_spec.index((words,tag))+1][0],"Expr"),tagged_words_spec.index((words,tag))) for (words,tag) in tagged_words_spec  if tag!="PERSON" and '-' in words]
	words_spec_parsed=[((words,"O"),tagged_words_spec.index((words,tag))) for (words,tag) in tagged_words_spec if  (words,tag) not in Expression and (words,tag) not in Acronym and (words,tag) not in Person_tagged]
	indice=[]
	for i in range(10):
		r=random.randint(0,len(words_spec_parsed)-1)
		indice.append(words_spec_parsed[r])
	result_summary=Person_tagged+indice+Expression+Acronym
	result_sorted= sorted(list(set(result_summary)),key=itemgetter(1))
	return [words for (words, num)in result_sorted]
	
	def find_patern(list_tokens_topics):
	i=0
	list_patern=[]
	while i<len(list_tokens_topics)-3:
		if "O"==list_tokens_topics[i][1] and "O"==list_tokens_topics[i+1][1] and "O"==list_tokens_topics[i+2][1]:
			list_patern.append(i)
			i+=1
		else:
			i+=1
	return list_patern



"""in an expression, we try to see if wikipedia find more results for not linked terms """
def decide_for_search(expr):
	if len(wikipedia.search(expr))<len(wikipedia.search(expr.replace('-',' '))):
		return expr.replace('-',' ')
	else:
		return expr
#patern= find_patern(list_tokens_topics)
"""Find categories from the extracted topics labelled with Epr, Pers, and O"""
def categorized_from_expr(list_tokens_topics):
	Expr_to_page={}
	for i in range(len(list_tokens_topics)):
		if  list_tokens_topics[i][1]=='Expr':
			Expr_to_page[list_tokens_topics[i][0]]=wikipedia.search(decide_for_search(list_tokens_topics[i][0]),2)
	return Expr_to_page

def categorized_from_people_org(list_tokens_topics):
	People_to_page={}
	for i in range(len(list_tokens_topics)):
		if  list_tokens_topics[i][1]=='Pers':
			People_to_page[list_tokens_topics[i][0]]=wikipedia.search(list_tokens_topics[i][0],1)
	return People_to_page



def  categorized_from_pattern(list_tokens_topics):
	Pattern_to_page={}
	if find_patern(list_tokens_topics)!=[]:
		for i in range(len(find_patern(list_tokens_topics))):
			Pattern_to_page[list_tokens_topics[i][0]+' '+list_tokens_topics[i+1][0]+' '+list_tokens_topics[i+2][0]]=wikipedia.search(list_tokens_topics[i][0]+' '+list_tokens_topics[i+1][0]+' '+list_tokens_topics[i+2][0])
	return Pattern_to_page



#l2=get_tokens_topics(text2)
#l1=get_tokens_topics(text3)

"""Find the topics of the text with the wikipedia.search instance (alternative version of topics_recovery to see which 
one is the better)"""

def topics_recovery_search(text):
	list_tokens_topics=get_tokens_topics(text)
	list_topics_from_expr=[]
	list_topics_from_people=[]
	for  value in categorized_from_expr(list_tokens_topics).values():
		try:
			for value_ in value:
				if len(value_.split())<=4:
					list_topics_from_expr+=[w for w in wikipedia.search(value_) if len(w.split())<=3 and 'article' not in w.lower()]
		except wikipedia.exceptions.DisambiguationError:
			pass
	for value in categorized_from_people_org(list_tokens_topics).values():
		try:
			for value_ in value:
				list_topics_from_people+=[w for w in wikipedia.search(value_) if len(w.split())<=3 and 'article' not in w.lower() and "CS1" not in w]
		except wikipedia.exceptions.DisambiguationError:
			#print(value_+' '+text.split()[text.split().index(value_)+1])
			l= wikipedia.search(value_+' '+text.split()[text.split().index(value_)+1])[0:2] 
			if   l!=[]:
				list_topics_from_people+=[w for w in wikipedia.search(l[0])]
	return list_topics_from_expr+list_topics_from_people

technology=wn.synset("technology.n.01")
science=wn.synset('science.n.01')
innovation=wn.synset('innovation.n.01')

"""find the token most related to the text and close to science, innovation and technology. We use this general token 
to re;ove the default category/ defaut search"""
def ref_word(text):
	distance_tech=[]
	distance_science=[]
	distance_innov=[]
	l=topics_recovery_search(text)
	for words in l:
		try:
			words_syn=wn.synset(words+'.n.01')
			distance_science.append((words_syn.path_similarity(science),words))
			distance_tech.append((words_syn.path_similarity(technology),words))
			distance_innov.append((words_syn.path_similarity(innovation),words))
		except reader.wordnet.WordNetError:
			pass
	max_science=sorted(distance_science,key=itemgetter(0))
	max_tech=sorted(distance_tech,key=itemgetter(0))
	max_innov=sorted(distance_innov,key=itemgetter(0))
	return ([max_tech[len(max_tech)-1],max_science[len(max_science)-1],max_innov[len(max_innov)-1]],l)


# def get_unique_words_from_recovery(list_recov):
# 	for i in range(len(list_recov)):
# 		list_recov[i]=(list_recov[i],i)
# 		if ' '  in word:
# 			new_word=word.replace(' ' ,',').split(",")
# 			list_recov.remove(word)
# 			for i in range(len(new_word)):
# 				list_recov.append(new_word[i])
# 	return list_recov

def remove_default_topics(text):
	(words,topics)= ref_word(text)
	word_ref=sorted(words,key=itemgetter(0))[len(words)-1][1]
	word_syn=wn.synset(word_ref+'.n.01') 
	distance=[]
	for topic in get_unique_words_from_recovery(topics):
		try:
			topic_syn=wn.synset(topic+'.n.01')
			distance.append((topic_syn.path_similarity(word_syn),topic))
		except reader.wordnet.WordNetError:
			pass
	sorted_distance=sorted(distance,key=itemgetter(0))
	n=len(sorted_distance)
	return sorted_distance  #10 has to be changed, can't adapt to every cases!









def get_unique_words_from_recovery(list_recov):
	cpy_recov=[]
	for i in range(len(list_recov)):
		cpy_recov.append(list_recov[i])
	for i in range(len(cpy_recov)):
		if ' ' not in cpy_recov[i]:
			list_recov[i]=( cpy_recov[i],i)
		if ' '  in cpy_recov[i]:
			new_word=cpy_recov[i].replace(' ' ,',').split(",")
			list_recov.remove(cpy_recov[i])
			for i in range(len(new_word)):
				list_recov.append((new_word[i],i))
 	return sorted(list_recov,key=itemgetter(1))













# def get_unique_words_from_recovery(list_recov):
# 	for word in list_recov:
# 		if ' '  in word:
# 			new_word=word.replace(' ' ,',').split(",")
# 			list_recov.remove(word)
# 			for i in range(len(new_word)):
# 				list_recov.append(new_word[i])
# 	return list_recov


# def Most_Common(lst):
# 	stemmer = SnowballStemmer("english")
# 	for i in range(len(lst)):
# 		lst[i]=stemmer.stem(lst[i])
#     	data = Counter(lst)
#     	data1=Counter(lst.remove(data.most_common(1)[0][0]))
#     	print(data1,data)
#     	return data.most_common(1)[0][0],data1.most_common(1)[0][0]
