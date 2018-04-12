import time
import requests
from openpyxl import *
import pandas as pd
from lxml import html
from bs4 import BeautifulSoup
import psycopg2

'''def get_connection():
	try:
		conn=psycopg2.connect(dbname='yvp4',user='postgres',password='harshit24')
		return conn
	except:
		print("Database Connection Failed.....")
		return
'''

def set_url(url):
	social_blade_url = "https://socialblade.com/youtube/"+url.rsplit("/",2)[1]+"/"+url.rsplit("/",2)[2]
	try:	
		session_requests = requests.session()
		res = session_requests.get(social_blade_url)
	except:
		print("Check connection")
		
	soup = BeautifulSoup(res.content, "html.parser")			
	#print(get_image(soup))
	#print(get_category(soup))
	#print(get_video_url(soup))
	return get_image(soup),get_category(soup),get_video_url(soup)
'''	conn1=get_connection()
	cur2=conn1.cursor()
	cur2.execute("update users_user_channel_main set channel_image_url = '%s',category = '%s',channel_url = '%s' where id =%d"%(str(get_image(soup)),str(get_category(soup)),str(get_video_url(soup)),id))
	conn1.commit()
'''
	

def get_image(soup):
	img_tag = soup.find("img",  {"id": "YouTubeUserTopInfoAvatar"})	
	return img_tag['src']
	
def get_category(soup):
	anchor_tag = soup.find("a",{"id":"youtube-user-page-channeltype"})
	return anchor_tag.text
	
def get_video_url(soup):
	video_url = soup.find("a", class_="core-button -margin core-small-wide ui-black")
	return video_url['href']

if __name__ == "__main__":
	'''conn=get_connection()
	cur1=conn.cursor()
	cur1.execute("select * from users_user_channel_main where channel_image_url = ''")
	data=cur1.fetchall()
	for d in data:
		set_url(d[0],d[3])
	'''
	set_url("https://www.youtube.com/user/corycotton")
	set_url("https://www.youtube.com/channel/UCegkCGMtLPrDrR7CuOIMgqQ")