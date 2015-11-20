#!/usr/bin/python
#-*-coding:utf-8-*-

from pymongo import Connection

con = Connection()#链接数据库，需要保证第一步已完成
db = con.test#链接test数据库

#百度歌手和歌曲库
baidu_Post = db.baidu
baidu_song_Post = db.baidu_songs

#腾讯歌手和歌曲库
qq_Post = db.qq
qq_song_Post = db.qq_songs

#咪咕音乐歌手和歌曲库
migu_Post = db.migu
migu_song_Post = db.mugu_songs

#查询方法
t = qq_Post.find({'queryname':'五月天'})#查询包含queryname这个key的值为五月天的所有记录，t是一个字典数组
t = qq_Post.find()#t 为qq歌手库的全部数据