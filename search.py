from nltk.corpus import stopwords
import re
import time
import sys
import os
import math
from collections import defaultdict,Counter
import operator
from nltk.stem import SnowballStemmer

def findFileNo(low, high, offset, word, file, typ):
	ret=[]
	retv=-1
	counter=0
	while low < high:
		mid = int((low + high) / 2)
		counter+=1
		#print(counter)
		file.seek(offset[mid])
		wordPtr = file.readline().strip().split()
		if typ:
			word=int(word)
			wordPtr[0]=int(wordPtr[0])
		if word == wordPtr[0]:
			ret=wordPtr[1:]
			retv=mid
			break
		elif word < wordPtr[0]:
			high = mid
		else:
			low = mid + 1
	return ret, retv

def findDocs(filename, fileNo, field, word, fieldFile):
	fieldOffset = list()
	docFreq = list()
	f=open('./data/offset_' + field + fileNo + '.txt')
	for line in f:
		temp = line.strip().split()
		fieldOffset.append(int(temp[0]))
		docFreq.append(int(temp[1]))
	docList, mid = findFileNo(0, len(fieldOffset), fieldOffset, word, fieldFile,0)
	return docList, docFreq[mid]

def rank(results, docFreq, nfiles, qtype):
	queryIdf = {}
	for key in docFreq:
		docFreq[key] = math.log(float(nfiles) / float(docFreq[key]))
		queryIdf[key] = math.log((float(nfiles) - float(docFreq[key]) + 0.5))
		queryIdf[key] = queryIdf[key] / (float(docFreq[key]) + 0.5)
	docs = defaultdict(float)
	for word in results:
		for field in results[word]:
			if len(field) > 0:
				if field == 't':
					factor = 0.3
				elif field == 'b':
					factor = 0.25
				elif field == 'i':
					factor = 0.20
				elif field == 'c':
					factor = 0.1
				elif field == 'r':
					factor = 0.05
				elif field == 'l':
					factor = 0.05
				postingList = results[word][field]
				for i in range(0,len(postingList),2):
					docs[postingList[i]] += float( factor * float(1+math.log(float(postingList[i+1]))) * docFreq[word])
	return docs

def query_func(words, fvocab, type, fields):
	docFreq = {}
	counter=0
	docList = defaultdict(dict)
	for word in words:
		docs, mid = findFileNo(0, len(offset), offset, word, fvocab,0)
		if len(docs) > 0:
			if type==1:
				field=fields[counter]
				counter+=1
				fieldFile = open('./data/'+field + str(docs[0]) + '.txt', 'r')
				returnedList, df = findDocs('./data/'+field + str(docs[0]) + '.txt', docs[0], field, word, fieldFile)
				docList[word][field] = returnedList
				docFreq[word] = df
			else:
				docFreq[word] = docs[1]
				for field in fields:
					fieldFile = open('./data/'+field + str(docs[0]) + '.txt', 'r')
					returnedList, _ = findDocs('./data/'+field + str(docs[0]) + '.txt', docs[0], field, word, fieldFile)
					docList[word][field] = returnedList
	return docList, docFreq

def pre_processing(dat,type=0):
	stop_words=set(stopwords.words('english'))
	if type==0:
		dat=dat.strip().encode("ascii",errors="ignore").decode()
		dat=re.sub('&nbsp;|&lt;|&gt;|&amp;|&quot;|&apos;|&cent;|&pound;|&yen;|&euro;|&copy;|&reg;',' ',dat)
		dat=re.sub('\`|\~|\!|\@|\#|\"|\'|\$|\%|\^|\&|\*|\(|\)|\-|\_|\=|\+|\\|\||\]|\[|\}|\{|\;|\:|\/|\?|\.|\>|\,|\<|\'|\n|\||\|\/"',' ',dat)
		dat=dat.split()
	final_data=[]
	ss=SnowballStemmer('english')
	for w in dat:
		if not w.strip() in stop_words:
			w=ss.stem(w)
			final_data.append(w)
	return final_data

def get_files():
	file=open('./data/titleOffset.txt','r')
	for lines in file:
		title_offset.append(int(lines.strip()))
	file=open('./data/offset.txt','r')
	for lines in file:
		offset.append(int(lines.strip()))
	titleFile=open('./data/title.txt','r')
	fvocab=open('./data/vocab.txt','r')
	file=open('./data/fileNumbers.txt','r')
	nfiles=int(file.read().strip())
	return title_offset,offset,titleFile,fvocab,nfiles

def main():
	key_words=['title','body','infobox','category','ref','links']
	title_offset,offset,titleFile,fvocab,nfiles=get_files()
	while True:
		query=input("Query: ")
		start_time=time.time()
		query=query.lower()
		query=query.strip()
		if query=='exit()':
			break
		temp=query.split(':')
		if temp[0] in key_words:
			query_type=1 #Field query
		else:
			query_type=0
		if not query_type:
			tokens=pre_processing(query)
			results, docFreq = query_func(tokens,fvocab,0,['t', 'b', 'i', 'c', 'r', 'l'])
			results = rank(results,docFreq,nfiles,0)			
		else:
			tempFields = list()
			tokens = list()
			temp=re.split(":| ",query)
			ip=defaultdict(str)
			for i in temp:
				if i in key_words:
					key_word=i
				else:
					ip[key_word]=ip[key_word]+str(i)+' '
			for i in ip:
				ip[i]=ip[i].strip()
				ip[i]=pre_processing(ip[i])
			tempFields=list(ip)
			for key in tempFields:
				tokens.append(' '.join(ip[key]))
			for i in range(len(tempFields)):
				if tempFields[i]=='title':
					tempFields[i]='t'
				elif tempFields[i]=='body':
					tempFields[i]='b'
				elif tempFields[i]=='category':
					tempFields[i]='c'
				elif tempFields[i]=='info':
					tempFields[i]='i'
				elif tempFields[i]=='links':
					tempFields[i]='l'
				elif tempFields[i]=='ref':
					tempFields[i]='r'
			results, docFreq = query_func(tokens, fvocab, 1, tempFields)
			results = rank(results,docFreq,nfiles,0)
		print('\nResults:')
		if len(results) > 0:
			results = sorted(results, key=results.get, reverse=True)
			results = results[:10]
			for i in range(len(results)):
				title, _ = findFileNo(0, len(title_offset), title_offset, results[i], titleFile, 1)
				print(' '.join(title))
		else:
			print("NO RELEVANT RESULTS FOUND!!!")
		print('\nTime: ', time.time()-start_time)
		print("\n")

if __name__ == '__main__':
	global offset,title_offset
	title_offset=[]
	offset=[]
	main()