#!/usr/bin/python
#-*-coding:utf-8-*-

import re
import anydbm
import urllib2
import urllib
import time
from pymongo import Connection
import chardet
import random


def baidu(songname,qt):

	time.sleep(random.randint(2, 5))
	#url='http://music.baidu.com/search/song?key=%s&s=1'%songname
	url = 'http://music.baidu.com/search?key=%s'%songname
	f=urllib.urlopen(url)
	data=re.sub('\n|\r','',f.read())
	#print data
	f.close()
	mat=re.compile(r'<span class=\"index-num index-hook\"(.*?)<input type=\"checkbox\"   class=\"checkbox-item-hook\"').findall(data)
	t = time.strftime("%Y-%m-%d %A", time.localtime()) 
	datahash = {}
	datahash['source'] = 'baidu'
	datahash['queryname'] = songname
	datahash["time"] = t
	datahash["queryType"] = qt
	outmat=[]
	c = 0
	for i in mat:
		songid = ''
		song=''
		singer=''
		album=''
		songmat=re.compile(r'<span class=\"song-title\".*? \"id\": \"(.*?)\" \}\'title=\"(.*?)\">').findall(i)
		if len(songmat)>0:
			if re.search('审批',songmat[0][1]):
				song_temp=re.compile('审批').split(songmat[0][1])
				song=song_temp[0][1]
				songid = song_temp[0][0]
			else:
				song=songmat[0][1]
				songid = songmat[0][0]
		try:
			url = "http://music.baidu.com/song/"+songid
			f=urllib.urlopen(url)
			data=re.sub('\n|\r','',f.read())
			f.close()
			mat = re.compile(r"<span class=\"song-play-num hot-num\">.*?<span class=\"c6\">.*?</span><span class=\"num\">(.*?)</span>").findall(data)
			if len(mat) > 0:
				hot = mat[0]
			else:
				hot = 'nil'
		except:
			hot = 'nil'
		singermat=re.compile(r'<span class=\"singer.*?title=\"(.*?)\">').findall(i)
		if len(singermat)>0:singer=singermat[0]
		'''
		albummat=re.compile(r'<span class=\"album-title\".*?title=\"(.*?)\">.*?<span class="music-icon-hook"').findall(i)
		if len(albummat)>0:
			if not re.search('href',albummat[0]):
				album=albummat[0]
		'''
		try:
			song = song.decode('gbk').encode('utf-8')
		except:
			song = song

		try:
			singer = singer.deocde('gbk').encode('utf-8')
		except:
			singer = singer
		if re.search(r'\.',song):continue

		temphash = {}
		if not re.search('\d',songid):continue
		temphash[songid] = {}
		temphash[songid]['songname'] = song
		temphash[songid]['singername'] = singer
		temphash[songid]['hot'] = hot
		outmat.append(temphash)
		c += 1
		#outstr='song:'+song+'	singer:%s'%singer+'	id:%s'%songid+'	hot:%s'%hot
		#outmat.append(outstr.decode('utf-8').encode('gbk')
		#outmat.append(outstr)
		if c == 21:break
	datahash['songs'] = outmat
	return datahash

def tencent(queryname,qt):
	time.sleep(2)
	encodestr = urllib.quote(queryname)
	url = 'http://soso.music.qq.com/fcgi-bin/multiple_music_search.fcg?mid=1&p=1&catZhida=1&lossless=0&t=100&searchid=27307080004708261&remoteplace=txt.yqqlist.top&utf8=1&w=%s'%queryname
	f=urllib.urlopen(url)
	data=re.sub('\n|\r','',f.read())
	f.close()
	t = time.strftime("%Y-%m-%d %A", time.localtime()) 
	datahash = {}
	datahash['source'] = 'qq'
	datahash['queryname'] = queryname
	datahash["time"] = t
	datahash["queryType"] = qt
	outmat=[]
	#mat = re.compile(r'<li class=\".*?_category\" onmouseover.*?>(.*?)</li>').findall(data)
	mat = re.compile(r'<a class=\"data\" style=\"display:none;\">(.*?)</a>').findall(data)
	for i in mat:
		songid = ''
		song=''
		singer=''
		album=''
		d = re.compile(r'\|').split(i)
		if len(d) < 5:continue
		songid = d[0]
		song = d[1]
		singer = d[3]
		album = d[5]
		temphash = {}
		temphash[songid] = {}
		try:
			temphash[songid]['songname'] = song.decode('gbk').encode('utf-8')

			temphash[songid]['singername'] = singer.decode('gbk').encode('utf-8')
			temphash[songid]['albumname'] = album.decode('gbk').encode('utf-8')
		except:
			continue
		#temphash[songid]['hot'] = hot
		outmat.append(temphash)


	datahash['songs'] = outmat
	return datahash

def migu(queryname,qt):
	time.sleep(2)
	url = 'http://music.migu.cn/webfront/search/uss.do?keyword=%s&keytype=song&pagesize=20&pagenum=1'%queryname
	f=urllib.urlopen(url)
	data=re.sub('\n|\r','',f.read())
	f.close()
	mat = re.compile(r'<li>(.*?)</li>').findall(data)
	mat2 = re.compile(r'<li class=\"fl current\">.*?歌曲（(.*?)） .*?</li>').findall(data)
	t = time.strftime("%Y-%m-%d %A", time.localtime())
	datahash = {}
	datahash['source'] = 'migu'
	datahash['queryname'] = queryname
	datahash["time"] = t
	datahash["queryType"] = qt
	datahash['totalResult'] = mat2[0]
	outmat=[]
	for i in mat:
		songid = ''
		song=''
		singer=''
		album=''
		hot = ''
		songmat = re.compile(r'<span class=\"fl song_name\">.*?#/song\/(.*?)\/.*?title=\"(.*?)\">.*?</a>').findall(i)
		if len(songmat) > 0:
			songid = songmat[0][0]
			song = songmat[0][1]
		else:
			continue
		hotmat = re.compile(r'<span class=\"fl songlist_jdt mr10\">.*?style=\"width:(.*?)%\">').findall(i)
		if len(hotmat) > 0:
			hot = hotmat[0]
		else:
			continue

		singermat = re.compile(r'<span class=\"fl singer_name mr5\">.*?title=\"(.*?)\">.*?</a>').findall(i)
		if len(singermat) > 0:
			singer = singermat[0]
		else:
			continue
		if re.search(r'\.',song):continue

		temphash = {}
		temphash[songid] = {}
		temphash[songid]['songname'] = song
		temphash[songid]['singername'] = singer
		temphash[songid]['hot'] = hot
		outmat.append(temphash)

	datahash['songs'] = outmat
	return datahash

def main(songfile,singerfile):

	today = '2015-01-19 Monday'
	con = Connection()
	db = con.test
	
	baidu_Post = db.baidu
	baidu_song_Post = db.baidu_songs

	qq_Post = db.qq
	qq_song_Post = db.qq_songs

	migu_Post = db.migu
	migu_song_Post = db.mugu_songs

	c = 0
	songdata = open(songfile,'r')
	for i in songdata:
		c += 1
		
		try:
			query = i.strip('\n')
			query_print = query.decode('utf-8')
		except:
			continue
		t_baidu = baidu_song_Post.find({"queryname":query,'time':today}).count()
		t_qq = qq_song_Post.find({"queryname":query,'time':today}).count()
		t_migu = migu_song_Post.find({"queryname":query,'time':today}).count()
		'''
		try:
			if t_baidu == 0:
				datahash_baidu = baidu(query,'song')
				baidu_song_Post.insert(datahash_baidu)
				print 'baidu done'
			else:
				print 'baidu finish'
		except:
			print 'baidu coding error'
		'''
		try:
			if t_qq == 0:
				datahash_qq = tencent(query,'song')
				qq_song_Post.insert(datahash_qq)
				print 'qq done'
			else:
				print 'qq finish'
		except:
			print 'qq coding error'
	
		try:
			if t_migu == 0:
				datahash_migu = migu(query,'song')
				#print datahash_migu
				migu_song_Post.insert(datahash_migu)
				print 'migu done'
			else:
				print 'migu finish'
		except:
			print 'migu coding error'
		
		try:
			print 'baidu_song:',baidu_song_Post.find().count(),' qq_song:',qq_song_Post.find().count(),' migu_song:',migu_song_Post.find().count(),' current:',c,' query:',query_print,'\n'
		except:
			print 'print error'
	singerdata = open(singerfile,'r')
	c = 0
	for j in singerdata:
		c += 1
		
		try:
			query = j.strip('\n')
			query_print = query.decode('utf-8')
		except:
			continue
		t_baidu = baidu_Post.find({"queryname":query,'time':today}).count()
		t_qq = qq_Post.find({"queryname":query,'time':today}).count()
		t_migu = migu_Post.find({"queryname":query,'time':today}).count()
		'''
		try:
			if t_baidu == 0:
				datahash_baidu = baidu(query,'singer')
				baidu_Post.insert(datahash_baidu)
				print 'baidu done'
		except:
			print 'baidu coding error'
		'''
		try:
			if t_qq == 0:
				datahash_qq = tencent(query,'singer')
				qq_Post.insert(datahash_qq)
				print 'qq done'
		except:
			print 'qq coding error'
		
		try:
			if t_migu == 0:
				datahash_migu = migu(query,'singer')
				migu_Post.insert(datahash_migu)
				print 'migu done'
		except:
			print 'migu coding error'
		
		
		try:
			print 'baidu_singer:',baidu_Post.find().count(),' qq_singer:',qq_Post.find().count(),' migu_singer:',migu_Post.find().count(),' current:',c,' query:',query_print
		except:
			print 'print error'



if __name__=='__main__':
	t = time.strftime("%Y-%m-%d %A", time.localtime())
	main('searchSong.txt','searchSinger.txt')
	'''
	con = Connection()
	db = con.test
	t = db.qq.find({'queryname':'五月天'})


	for myhash in t:
		print 'queryname:',myhash['queryname'].encode('utf-8')
		print 'time:',myhash['time']
		print 'source:',myhash['source']
		print 'queryType:',myhash['queryType']
		print 'songs:'
		for k in myhash['songs']:		
			for j in k:
				print 'id:'+j.encode('utf-8')+'	songname:'+k[j]['songname'].encode('utf-8')+'	singername:'+k[j]['singername'].encode('utf-8')+'	albumname:'+k[j]['albumname'].encode('utf-8')
		print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
	'''
