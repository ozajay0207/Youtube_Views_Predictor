import time
import requests
from openpyxl import *
import pandas as pd
from lxml import html
from bs4 import BeautifulSoup

def set_url(url):	
	social_blade_url = "https://socialblade.com/youtube/"+url.rsplit("/",2)[1]+"/"+url.rsplit("/",2)[2]
	try:	
		session_requests = requests.session()
		res = session_requests.get(social_blade_url)
	except:
		print("Check connection")
		
	soup = BeautifulSoup(res.content, "html.parser")			
	print(get_image(soup))
	print(get_category(soup))
	print(get_video_url(soup))
	
	
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
	set_url("https://www.youtube.com/user/corycotton")
	set_url("https://www.youtube.com/channel/UCegkCGMtLPrDrR7CuOIMgqQ")
	
	