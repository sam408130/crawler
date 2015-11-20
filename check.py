#!/usr/bin/python
#-*-coding:utf-8-*-

import re
import anydbm
import time
from pymongo import Connection

def levenshtein(first,second):  
	if len(first) > len(second):  
		first,second = second,first  
	if len(first) == 0:  
		return len(second)  
	if len(second) == 0:  
		return len(first)  
	first_length = len(first) + 1  
	second_length = len(second) + 1  
	distance_matrix = [range(second_length) for x in range(first_length)]   
	#print distance_matrix  
	for i in range(1,first_length):  
		for j in range(1,second_length):  
			deletion = distance_matrix[i-1][j] + 1  
			insertion = distance_matrix[i][j-1] + 1  
			substitution = distance_matrix[i-1][j-1]  
			if first[i-1] != second[j-1]:  
				substitution += 1  
			distance_matrix[i][j] = min(insertion,deletion,substitution)  
	#print distance_matrix  
	return distance_matrix[first_length-1][second_length-1]  
def getKeys(mat):
	keymat = []
	c = 0
	for i in mat:
		c += 1
		if c > 20:break
		keymat.append(i.keys()[0])
	return keymat
def prohash(inhash,t,d,l):
	if t != 'nil':
		if inhash['totalmax'] < t:
			inhash['totalmax'] = t
		if inhash['totalmin'] < t:
			inhash['totalmin'] = t
	if d != 'nil':
		if inhash['dif'].has_key(d):
			inhash['dif'][d] += 1
		else:
			inhash['dif'][d] = 1
	if inhash['ld'].has_key(l):
		inhash['ld'][l] += 1
	else:
		inhash['ld'][l] = 1
	return inhash
def parse(hashmat):
	l = hashmat.count() 	
	try:
		total_0 = int(hashmat[0]['totalResult'])
		total_1 = int(hashmat[l-1]['totalResult'])
		if total_0 == 0 and total_1 > 0:print '~~~'+hashmat[0]['queryname']
		dif = total_0 - total_1
	except:
		total_1 = 'nil'
		dif = 'nil'
	ld = levenshtein(getKeys(hashmat[0]['songs']),getKeys(hashmat[l-1]['songs']))
	return total_1,dif,ld

def prohash2(inhash):
	keys = sorted(inhash.iteritems(),key=lambda inhash:inhash[1],reverse=True)
	c = 0
	for i in keys:
		c += 1
		#if c >= 10:break
		print i[0],i[1]
def main():
	con = Connection()
	db = con.test
	myhash_song = {}
	myhash_singer = {}
	myhash_song['totalmax'] = 0
	myhash_song['totalmin'] = 1000
	myhash_song['dif'] = {}
	myhash_song['ld'] = {}
	myhash_singer['dif'] = {}
	myhash_singer['ld'] = {}
	myhash_singer['totalmax'] = 0
	myhash_singer['totalmin'] = 1000
	songs = open('searchSong.txt','r')
	singers = open('searchSinger.txt','r')
	migu_Post = db.migu
	migu_song_Post = db.mugu_songs
	lable = 1
	d = 0
	for i in songs:
		query = i.strip('\n')
		hashmat = migu_song_Post.find({"queryname":query})
		if hashmat.count() > 0:d += 1
		if lable == 1:
			print hashmat.count()
			lable += 1
		try:
			total,dif,ld = parse(hashmat)
			print ld,dif,query
		except:
			continue
		myhash_song = prohash(myhash_song,total,dif,ld)
	lable = 1
	for i in singers:
		query = i.strip('\n')
		hashmat = migu_Post.find({"queryname":query})
		if lable == 1:
			print hashmat.count()
			lable += 1
		try:
			total,dif,ld = parse(hashmat)
			print ld,dif,query
		except:
			continue
		myhash_singer = prohash(myhash_singer,total,dif,ld)

	print 'singer_totalmax:',myhash_singer['totalmax'],'	song_totalmax:',myhash_song['totalmax']
	print 'singer_totalmin:',myhash_singer['totalmin'],'	song_totalmin:',myhash_song['totalmin']
	print '----------------------song dif---------------------'
	prohash2(myhash_song['dif'])
	print '----------------------singer dif-------------------'
	prohash2(myhash_singer['dif'])
	print '----------------------song ld----------------------'
	prohash2(myhash_song['ld'])
	print '----------------------singer ld--------------------'
	prohash2(myhash_singer['ld'])
	
if __name__ == '__main__':
	main()





