import xml.sax
import sys
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
from collections import defaultdict
import re
import time
import os
import operator

stop_words=set(stopwords.words('english'))
titles=[]
start_time=time.time()
index_map=defaultdict(list)
dictID={}
no_of_pages=0
file_count=0
offset=0

def create_index(title,body,infobox,categories,external_links,references):
	global no_of_pages
	global index_map
	global file_count
	global dictID
	global offset

	words=defaultdict(int)	
	
	title_dict=defaultdict(int)
	for i in range(len(title)):
		title_dict[title[i]]+=1
		words[title[i]]+=1

	body_dict=defaultdict(int)
	for i in range(len(body)):
		body_dict[body[i]]+=1
		words[body[i]]+=1
	
	infobox_dict=defaultdict(int)
	for i in range(len(infobox)):
		infobox_dict[infobox[i]]+=1
		words[infobox[i]]+=1

	categories_dict=defaultdict(int)
	for i in range(len(categories)):
		categories_dict[categories[i]]+=1
		words[categories[i]]+=1

	external_links_dict=defaultdict(int)
	for i in range(len(external_links)):
		external_links_dict[external_links[i]]+=1
		words[external_links[i]]+=1

	references_dict=defaultdict(int)
	for i in range(len(references)):
		references_dict[references[i]]+=1
		words[references[i]]+=1

	no_of_pages+=1
	
	for word in words.keys():
            temp = 'd'+str(no_of_pages-1)
            if title_dict[word]:
                temp += 't' + str(title_dict[word])
            if body_dict[word]:
                temp += 'b' + str(body_dict[word])
            if infobox_dict[word]:
                temp += 'i' + str(infobox_dict[word])
            if categories_dict[word]:
                temp += 'c' + str(categories_dict[word])
            if external_links_dict[word]:
                temp += 'l' + str(external_links_dict[word])
            if references_dict[word]:
                temp += 'r' + str(references_dict[word])

            index_map[word].append(temp)

	if not no_of_pages%25000:
		write_into_temp_files()
		

def write_into_temp_files():
	global index_map
	global file_count
	global dictID
	global offset
	data=[]
	prev_title_offset=offset
	for key in sorted(index_map.keys()):
		postings = index_map[key]
		string = key + ' '
		string += ' '.join(postings)
		data.append(string)

	with open('./data/index' + str(file_count) + '.txt', 'w') as file:
		file.write('\n'.join(data))

	dataOffset = []
	data = []
	for key in sorted(dictID):
		dataOffset.append(str(prev_title_offset))
		temp = str(key) + ' ' + dictID[key].strip()
		data.append(temp)
		prev_title_offset += len(temp) + 1

	with open('./data/title.txt', 'a') as file:
		file.write('\n'.join(data))
		file.write('\n')
    
	with open('./data/titleOffset.txt', 'a') as file:
		file.write('\n'.join(dataOffset))
		file.write('\n')

	offset = prev_title_offset
	index_map = defaultdict(list)
	dictID={}
	file_count+=1

def final_processing(data):
	data=data.strip().encode("ascii",errors="ignore").decode()
	#data=re.sub('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\), ]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',' ',data)
	data=re.sub(r'\`|\~|\!|\@|\#|\"|\'|\$|\%|\^|\&|\*|\(|\)|\-|\_|\=|\+|\\|\||\]|\[|\}|\{|\;|\:|\/|\?|\.|\>|\,|\<|\'|\n|\||\|\/"',r' ',data)
	data=re.sub(r'&nbsp;|&lt;|&gt;|&amp;|&quot;|&apos;|&cent;|&pound;|&yen;|&euro;|&copy;|&reg;',r' ',data)
	#Above code removes any special character
	final_data=[]
	ss=SnowballStemmer('english')
	data=data.split()
	for w in data:
		if not w.strip() in stop_words:
			w=ss.stem(w)
			final_data.append(w)
	return final_data
		
def get_infobar(data):
	data=data.split('\n')
	length=len(data)
	ret=[]
	flag=0
	for i in range(length):
		if flag%2==0 and re.search(r'\{\{infobox',data[i]):
			flag=1
			ret.append(re.sub(r'\{\{infobox','',data[i]))
		elif flag%2==1:
			if data[i]=='}}':
				flag=flag+1
				continue
			ret.append(data[i])
		elif flag==0:
			if i*100/length > 50:
				break

	return final_processing(' '.join(ret))

def get_categories(data):
	data=re.findall(r'\[\[category:.*\]\]',data)
	ret=[]
	for i in data:
		ret.append(i[11:len(i)-2])

	return final_processing(' '.join(ret))

def get_external_links(text):
	data=text.split('==external links==')
	if len(data)==1:
		data=text.split('==external links ==')	
	if len(data)==1:
		data=text.split('== external links==')
	if len(data)==1:
		data=text.split('== external links ==')
	if len(data)==1:
		return []
	data=data[1]
	data=re.findall(r'\*\s*\[.*\]',data)
	ret=[]
	for i in data:
		ret.append(i[2:len(i)-1])
	return final_processing(' '.join(ret))

def get_references(text):
	ret=[]
	data1=re.findall(r'\|\s*title[^\|]*',text)
	for i in data1:
		ret.append(i[i.find('=')+1:len(i)-1])
	return final_processing(' '.join(ret))

def process_text(text,title):
	text=text.lower()
	references=[]
	categories=[]
	external_links=[]
	data=text.split('==references==')
	if data[0]==text:
		data=text.split('==references ==')	
	if data[0]==text:
		data=text.split('== references==')
	if data[0]==text:
		data=text.split('== references ==')
	if data[0]==text:
		categories=get_categories(data[0])
		external_links=get_external_links(data[0])
	else:
		categories=get_categories(data[1])
		external_links=get_external_links(data[1])
		references=get_references(data[1])	

	info_bar=get_infobar(data[0])
	data[0]=re.sub(r'\{\{.*\}\}',r' ',data[0])
	body=final_processing(data[0])
	title=final_processing(title.lower())
	return title,body,info_bar,categories,external_links,references


class Handler(xml.sax.ContentHandler):
	def __init__(self):
		self.tag=""
		self.title=""
		self.text=""
		self.id=""
		self.idFlag=0#so that it does not read ids of revesion 

	def startElement(self,name,attrs):
		self.tag=name

	def endElement(self,name):
		global no_of_pages
		if name=='page':
			self.title=self.title.strip().encode("ascii",errors="ignore").decode()
			dictID[no_of_pages]=self.title
			title,body,infobox,categories,external_links,references=process_text(self.text,self.title)
			create_index(title,body,infobox,categories,external_links,references)
			self.tag=""
			self.title=""
			self.text=""
			self.id=""
			self.idFlag=0

	def characters(self, content):
		if self.tag == 'text':
			self.text+=content
		if self.tag == 'title':
			self.title+=content
		if self.tag == 'id' and self.idFlag==0:
			self.id = content
			self.idFlag=1

def FinalIndexCreator(data, finalCount, offsetSize):
	body = defaultdict(dict)
	title = defaultdict(dict)
	info = defaultdict(dict)
	distinctWords = []
	link = defaultdict(dict)
	reference = defaultdict(dict)
	category = defaultdict(dict)
	offset = []
    
	for key in sorted(data.keys()):
		temp = []
		docs = data[key]
        
		for i in range(len(docs)):
			docID = re.sub(r'.*d([0-9]*).*', r'\1', docs[i])
			temp = re.sub(r'.*t([0-9]*).*', r'\1', docs[i])
			posting = docs[i]
            
			if temp != docs[i]:
				temp=float(temp)
				title[key][docID] = temp
            
			temp = re.sub(r'.*b([0-9]*).*', r'\1', docs[i])
			if temp != docs[i]:
				temp=float(temp)
				body[key][docID] = temp

			temp = re.sub(r'.*i([0-9]*).*', r'\1', docs[i])
			if temp != docs[i]:
				temp=float(temp)
				info[key][docID] = temp

			temp = re.sub(r'.*c([0-9]*).*', r'\1', docs[i])
			if temp != docs[i]:
				temp=float(temp)
				category[key][docID] = temp

			temp = re.sub(r'.*l([0-9]*).*', r'\1', docs[i])
			if temp != docs[i]:
				temp=float(temp)
				link[key][docID] = temp
            
			temp = re.sub(r'.*r([0-9]*).*', r'\1', docs[i])
			if temp != docs[i]:
				temp=float(temp)
				reference[key][docID] = temp

		distinctWords.append(key + ' ' + str(finalCount) + ' ' + str(len(docs)))
		offset.append(str(offsetSize))
		offsetSize += len(key + ' ' + str(finalCount) + ' ' + str(len(docs))) + 1

	titleData = list()
	titleOffset = list()
	prevTitle = 0

	bodyData = list()
	bodyOffset = list()
	prevBody = 0
    
	infoData = list()
	infoOffset = list()
	prevInfo = 0
    
	linkData = list()
	linkOffset = list()
	prevLink = 0
    
	categoryOffset = list()
	categoryData = list()
	prevCategory = 0
    
	referenceOffset = list()
	referenceData = list()
	prevReference = 0

	for key in sorted(data.keys()):
		if key in title:
			string = key + ' '
			docs = sorted(title[key], key = title[key].get, reverse=True)
			for i in range(len(docs)):
				string += docs[i] + ' ' + str(title[key][docs[i]]) + ' '
			titleOffset.append(str(prevTitle) + ' ' + str(len(docs)))
			titleData.append(string)
			prevTitle += len(string) + 1

		if key in body:
			string = key + ' '
			docs = sorted(body[key], key = body[key].get, reverse=True)
			for i in range(len(docs)):
				string += docs[i] + ' ' + str(body[key][docs[i]]) + ' '
			bodyOffset.append(str(prevBody) + ' ' + str(len(docs)))
			bodyData.append(string)
			prevBody += len(string) + 1

		if key in info:
			string = key + ' '
			docs = sorted(info[key], key = info[key].get, reverse=True)
			for i in range(len(docs)):
				string += docs[i] + ' ' + str(info[key][docs[i]]) + ' '
			infoOffset.append(str(prevInfo) + ' ' + str(len(docs)))
			infoData.append(string)
			prevInfo += len(string) + 1

		if key in category:
			string = key + ' '
			docs = sorted(category[key], key = category[key].get, reverse=True)
			for i in range(len(docs)):
				string += docs[i] + ' ' + str(category[key][docs[i]]) + ' '
			categoryOffset.append(str(prevCategory) + ' ' + str(len(docs)))
			categoryData.append(string)
			prevCategory += len(string) + 1

		if key in link:
			string = key + ' '
			docs = sorted(link[key], key = link[key].get, reverse=True)
			for i in range(len(docs)):
				string += docs[i] + ' ' + str(link[key][docs[i]]) + ' '
			linkOffset.append(str(prevLink) + ' ' + str(len(docs)))
			linkData.append(string)
			prevLink += len(string) + 1

		if key in reference:
			string = key + ' '
			docs = sorted(reference[key], key = reference[key].get, reverse=True)
			for i in range(len(docs)):
				string += docs[i] + ' ' + str(reference[key][docs[i]]) + ' '
			referenceOffset.append(str(prevReference) + ' ' + str(len(docs)))
			referenceData.append(string)
			prevReference += len(string) + 1

	with open('./data/offset_b' + str(finalCount) + '.txt', 'w') as file:
		file.write('\n'.join(bodyOffset))
	with open('./data/b' + str(finalCount) + '.txt', 'w') as file:
		file.write('\n'.join(bodyData))

	with open('./data/offset_i' + str(finalCount) + '.txt', 'w') as file:
		file.write('\n'.join(infoOffset))
	with open('./data/i' + str(finalCount) + '.txt', 'w') as file:
		file.write('\n'.join(infoData))
	
	with open('./data/offset_t' + str(finalCount) + '.txt', 'w') as file:
		file.write('\n'.join(titleOffset))
	with open('./data/t' + str(finalCount) + '.txt', 'w') as file:
		file.write('\n'.join(titleData))

	with open('./data/offset_l' + str(finalCount) + '.txt', 'w') as file:
		file.write('\n'.join(linkOffset))
	with open('./data/l' + str(finalCount) + '.txt', 'w') as file:
		file.write('\n'.join(linkData))
	
	with open('./data/offset_r' + str(finalCount) + '.txt', 'w') as file:
		file.write('\n'.join(referenceOffset))
	with open('./data/r' + str(finalCount) + '.txt', 'w') as file:
		file.write('\n'.join(referenceData))

	with open('./data/offset_c' + str(finalCount) + '.txt', 'w') as file:
		file.write('\n'.join(categoryOffset))
	with open('./data/c' + str(finalCount) + '.txt', 'w') as file:
		file.write('\n'.join(categoryData))

	with open('./data/vocab.txt', 'a') as file:
		file.write('\n'.join(distinctWords))
		file.write('\n')

	with open('./data/offset.txt', 'a') as file:
		file.write('\n'.join(offset))
		file.write('\n')

	finalCount=finalCount+1    
	return finalCount, offsetSize


def merge_files(fileCount):
	flag = [0] * fileCount
	count = 0
	offsetSize = 0
	finalCount = 0
	data = defaultdict(list)
	array = list()
	words = {}
	files = {}
	top = {}

	for i in range(fileCount):
		files[i] = open('./data/index' + str(i) + '.txt', 'r')
		top[i] = files[i].readline().strip()
		flag[i] = 1
		words[i] = top[i].split()
		first = words[i][0]
		if first not in array:
			array.append(words[i][0])
	array.sort()
	while any(flag):
		count += 1
		temp = array[0]
		array.pop(0)
		if not count%100000:
			rrr = finalCount
			finalCount, offsetSize = FinalIndexCreator(data, finalCount, offsetSize)
			oldFileCount=rrr
			if oldFileCount != finalCount:
				data = defaultdict(list)
		for i in range(fileCount):
			if flag[i] and words[i][0] == temp:
				top[i] = files[i].readline()
				data[temp].extend(words[i][1:])
				top[i] = top[i].strip()
				if len(top[i]) == 0:
					print("SFFD")
					files[i].close()
					flag[i] = 0
					os.remove('./data/index' + str(i) + '.txt')
				else:
					words[i] = top[i].split()
					first=words[i][0]
					if first not in array:
						array.append(words[i][0]) 
						array.sort()  
	finalCount, offsetSize = FinalIndexCreator(data, finalCount, offsetSize)

def main():
	global no_of_pages
	global index_map
	global file_count
	global dictID
	global offset
	parser = xml.sax.make_parser()
	parser.setFeature(xml.sax.handler.feature_namespaces,False)
	handler = Handler()
	parser.setContentHandler(handler)
	output=parser.parse(sys.argv[1])
	
	with open('./data/fileNumbers.txt','w') as f:
		f.write(str(no_of_pages))

	write_into_temp_files()
	print("File COunt:"+str(file_count))
	merge_files(file_count)
	print("Finish")

if __name__ == '__main__':
	main()
