#engagmentfromlog:
"""instruction: First run process_log.py"""

def parse_url(s):
	l=[]
	for i in range(len(s)):
		if s[i]=='/':
			l.append(i)
	return s[l[1]:l[2]+1]


path="/Users/victorstorchan/Desktop/telepath_files/2016_06_15.log"
s=""
lines=open(path,'r')
for l in lines:
	s+=l
lines.close()
logs_str=s	
logs_list = [d.strip() for d in logs_str.splitlines()]
logs_json = [json.loads(i) for i in logs_list]

n=len(logs_json_processed)
"""meaningful_url stores all the meaningful url. 
For each page we need to define engagment. we build a dictionary of engagment, where the 
keys are the meaningful url and the values are dictionaries representing features for engagment.
To be clear: """
engagment={}
meaningful_url=[logs_json_processed[i]['url'] for i in range(n)]

for i in range(n):
	engagment[meaningful_url[i]]={}

for j in range(n):
	for i in range(len(logs_json)):
		if logs_json[i]['eventType']=="resource_add" and logs_json[i]['data']['url']==meaningful_url[j]:
			engagment[meaningful_url[j]]['resource_add_time']=logs_json[i]['ts']
		if logs_json[i]['eventType']=="resource_focus" and logs_json[i]['data']['url']==meaningful_url[j]:
			engagment[meaningful_url[j]]['resource_focus_time']=logs_json[i]['ts']
		if logs_json[i]['eventType']=="resource_history_item" and logs_json[i]['data']['url']==meaningful_url[j]:
			engagment[meaningful_url[j]]['resource_history_item']=(logs_json[i]['data']['historyItem']['lastVisitTime'],logs_json[i]['data']['historyItem']['visitCount'])
		if logs_json[i]['eventType']=="resource_unfocus" and logs_json[i]['data']['url']==meaningful_url[j]:
			engagment[meaningful_url[j]]["resource_unfocus_time"]=logs_json[i]['ts']
		if logs_json[i]['eventType']=="resource_remove" and logs_json[i]['data']['url']==meaningful_url[j]:
			engagment[meaningful_url[j]]["resource_remove_time"]=logs_json[i]['ts']

features_from_engagment={}
for j in range(n):
	features_from_engagment[meaningful_url[j]]={}
for j in range(n):
	features_from_engagment[meaningful_url[j]]['diff_focus_unfocus']=engagment[meaningful_url[j]]["resource_unfocus_time"]-engagment[meaningful_url[j]]['resource_focus_time']
	features_from_engagment[meaningful_url[j]]['diff_add_remove']=engagment[meaningful_url[j]]["resource_remove_time"]-engagment[meaningful_url[j]]['resource_add_time']
	features_from_engagment[meaningful_url[j]]['lastVisit']=engagment[meaningful_url[j]]['resource_history_item'][0]
	features_from_engagment[meaningful_url[j]]['visitCount']=engagment[meaningful_url[j]]['resource_history_item'][0]
	features_from_engagment[meaningful_url[j]]['weight']=features_from_engagment[meaningful_url[j]]['diff_focus_unfocus']+0.5*features_from_engagment[meaningful_url[j]]['diff_add_remove']+features_from_engagment[meaningful_url[j]]['lastVisit']+features_from_engagment[meaningful_url[j]]['visitCount']

"""Note: should change the formula"""

ranking_from_engagment={}
list_of_weight=[]
for j in range(n):
	list_of_weight.append((meaningful_url[j],features_from_engagment[meaningful_url[j]]['weight']))

list_of_weight_sorted=sorted(list_of_weight, key=lambda x: x[1])
for j in range(n):
	ranking_from_engagment[parse_url(list_of_weight_sorted[j][0])]=j+1

