''need to change the threshold, 
need to change the decision for the intersection of the summary.
need to weight the words
'''



from difflib import SequenceMatcher

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()
def is_similar(a,b):
	return similar(a,b)>0.6

def get_id_users():

def get_


"""To use it, define:
s1=readme(url)
s1.get_python_file()
s1.extract_meaningful_info()
s1.create_dico_of_features()

s2=readme(url)
s2.get_python_file()
s2.extract_meaningful_info()
s2.create_dico_of_features()

 intersec=intersect_dico(s1,s2)"""



class intersect_dico(object):
	def __init__(self,s1,s2):
		self.dictionary1=s1.dico
		self.dictionary2=s2.dico
	def intersection(self):
		keys1=self.dictionary1.keys()
		keys2=self.dictionary2.keys()
		n1_url=len(self.dictionary1.keys())
		n2_url=len(self.dictionary2.keys())
		self.similarlinks=[]
		for i in range(n1_url):
			for j in range(n2_url):
				for k in range(len(self.dictionary1[keys1[i]]['links'])):
					for l in range(len(self.dictionary2[keys1[j]]['links'])):
						if is_similar(self.dictionary1[keys1[i]]['links'][k][0],self.dictionary2[keys2[j]]['links'][l][0]):
							self.similarlinks.append(self.dictionary1[keys1[i]]['links'][k][0])
		self.associated_github=[]
		for i in range(n1_url):
			for j in range(n2_url):
				for k in range(len(self.dictionary1[keys1[i]]['associated_github'])):
					for l in range(len(self.dictionary2[keys1[j]]['associated_github'])):
						if is_similar(self.dictionary1[keys1[i]]['associated_github'][k],self.dictionary2[keys2[j]]['associated_github'][l]):
							self.associated_github.append(self.dictionary1[keys1[i]]['associated_github'][k])
		self.associated_website=[]
		for i in range(n1_url):
			for j in range(n2_url):
				for k in range(len(self.dictionary1[keys1[i]]['associated_website'])):
					for l in range(len(self.dictionary2[keys1[j]]['associated_website'])):
						if is_similar(self.dictionary1[keys1[i]]['associated_website'][k],self.dictionary2[keys2[j]]['associated_website'][l]):
							self.associated_website.append(self.dictionary1[keys1[i]]['associated_website'][k])
		self.technical=[]
		for i in range(n1_url):
			for j in range(n2_url):
				for k in range(len(self.dictionary1[keys1[i]]['technical'])):
					for l in range(len(self.dictionary2[keys1[j]]['technical'])):
						if is_similar(self.dictionary1[keys1[i]]['technical'][k],self.dictionary2[keys2[j]]['technical'][l]):
							self.technical.append(self.dictionary1[keys1[i]]['technical'][k])
		self.summarize=[]
		for i in range(n1_url):
			for j in range(n2_url):
				for k in range(len(self.dictionary1[keys1[i]]['summarize'])):
					for l in range(len(self.dictionary2[keys1[j]]['summarize'])):
						if is_similar(self.dictionary1[keys1[i]]['summarize'][k],self.dictionary2[keys2[j]]['summarize'][l]):
							self.summarize.append(self.dictionary1[keys1[i]]['summarize'][k]) 

	def print_intersection(self):
		l=[]
		l.append(len(self.summarize))
		l.append(len(self.associated_website))
		l.append(len(self.associated_github))
		l.append(len(self.similarlinks))
		l.append(len(self.technical))
		l.append(len(self.summarize))
		self.min_=min(l)
		if self.min_>3:#change the threshold later
			print('user{} has these similarities:{} {} {} {}'.format())
