import pandas as pd
import numpy as np
import pickle
import requests
import random
import time
import math
import sys
from users.models import video_main,video_sub,user_channel_main,user_channel_sub, users
from datetime import datetime
import users.find_by_channel_id as fid

API_KEYS = ["AIzaSyAgzszK84rYUM0ErWSdtiV-tyNGqGB3xFg","AIzaSyA3uNDJDl6WH0z8t9uB9pdmbIBpf54PVIE","AIzaSyCcLbOx4L6iTcS4NnvviLa1TfE7I1mnccU","AIzaSyAOpWL4ijH4vjO6sOF5ORIzohy_o2shL9s","AIzaSyCp8TYUqMn5LMgeHDvBcNcd2Y3pGbgVTAg"]
data={"V_id":[],"channelId":[],"publishedAt":[],"commentCount":[],"dislikeCount":[],"likeCount":[],"viewCount":[],"publishedAt":[],"categoryId":[],"ChannelPublishedAt":[],"channel_videoCount":[],"channel_subscriberCount":[],"channel_ViewCount":[]}
channel_dict = {}

# The function returns the final URL for request
def get_url(Video_urls):
    v_id =  ",".join(Video_urls)
    k = random.randint(0,4)
    API_KEY = API_KEYS[k]
    url = "https://www.googleapis.com/youtube/v3/videos?part=status,snippet,topicDetails,contentDetails,statistics&id="+v_id+"&key="+API_KEY
    return url

# This function populates the data dictionary
def add_data(i,key1,key2,key3="NA"):
    if key3!="NA":
        try:
            data[key1].append(i[key2][key3])
        except Exception:
            if key1 in ['viewCount', 'commentCount','dislikeCount','publishedAt','channel_videoCount','channel_subscriberCount']:
                print(i["id"])
                print(key1+"missing")
            data[key1].append(0)
    else:
        try:
            data[key1].append(i[key2])
        except:
            data[key1].append(None)

# The function is used to get the Video relevant data
def video_data(get_json):
    for i in get_json["items"]:

# -----------------------------------VIDEO RELATED FEATURES   ---------------------------------------------------------------------

        # add_data(i,key1="tags",key2="snippet",key3="tags")

        add_data(i,key1="commentCount",key2="statistics",key3="commentCount")

        add_data(i,key1="dislikeCount",key2="statistics",key3="dislikeCount")

        add_data(i,key1="V_id",key2='id')

        add_data(i,key1="categoryId",key2="snippet",key3="categoryId")

        add_data(i,key1="publishedAt",key2="snippet",key3="publishedAt")

        add_data(i,key1="likeCount",key2="statistics",key3="likeCount")

        add_data(i,key1="viewCount",key2="statistics",key3="viewCount")

        add_data(i,key1="channelId",key2="snippet",key3="channelId")

# It gets the channel relevant data

def channel_data():

    channel_id = ",".join(data["channelId"])

    k = random.randint(0,4)
    API_KEY = API_KEYS[k]
    url = "https://www.googleapis.com/youtube/v3/channels?part=snippet,statistics&id="+channel_id+"&key="+API_KEY
    # print(url)
    r = requests.get(url)
    get_json = r.json()

    if len(set(data["channelId"])) == len(data["channelId"]):
        for i in get_json["items"]:
            add_data(i,key1="ChannelPublishedAt",key2="snippet",key3="publishedAt")

            add_data(i,key1="channel_ViewCount",key2="statistics",key3="viewCount")
            add_data(i,key1="channel_subscriberCount",key2="statistics",key3="subscriberCount")
            add_data(i,key1="channel_videoCount",key2="statistics",key3="videoCount")
    else:
        for i in get_json["items"]:
            channel_dict[i["id"]]={}
            # add_data(i,key1="channelTitle",key2="snippet",key3="title")
            # add_data(i,key1="ChannelDescription",key2="snippet",key3="description")
            channel_dict[i["id"]]["ChannelPublishedAt"] = i["snippet"]["publishedAt"]
            channel_dict[i["id"]]["channel_ViewCount"] = i["statistics"]["viewCount"]
            channel_dict[i["id"]]["channel_subscriberCount"] = i["statistics"]["subscriberCount"]
            channel_dict[i["id"]]["channel_videoCount"] = i["statistics"]["videoCount"]
        # print(channel_dict)

        for j in data["channelId"]:
            add_data(channel_dict,key1="ChannelPublishedAt",key2=j,key3="ChannelPublishedAt")
            add_data(channel_dict,key1="channel_ViewCount",key2=j,key3="channel_ViewCount")
            add_data(channel_dict,key1="channel_subscriberCount",key2=j,key3="channel_subscriberCount")
            add_data(channel_dict,key1="channel_videoCount",key2=j,key3="channel_videoCount")



def get_months(x):
    return 12-x.month + 1 + (2016 - (x.year+1)+1)*12

def get_video_details(V_id,name,type,url1,request):
    category_dict  = {29:"Non-profits & Activism",28:"Science & Technology",27:"Education",26:"Howtostyle",25:"New&politics",24:"Entertainment",23:"Comedy",22:"People&blogs",20:"Gaming",19:"Travel&events",17:"Sports",15:"Pets&Animals",10:"Music",2:"Cars&vehicles",1:"Film&Animation"}
    url = get_url(V_id)
    #print("\n\nURL by which we can scrap the data:\n\n",url,"\n")
    #print("\n\nCollecting data .......\n\n")
    r = requests.get(url)
    get_json = r.json()
    # print(get_json)
    video_data(get_json)
    channel_data()

    view_count = data['viewCount']
    like_count = data['likeCount']
    dislike_count = data['dislikeCount']
    publish_date = data['publishedAt']
    category_no =data['categoryId']
    category = category_dict[int(category_no[0])]
    print(view_count,like_count,dislike_count,publish_date[0][:10],category)
    try:
        getobj=video_main.objects.get(youtube_url=url1,user_id=users.objects.get(pk=request.session['User_Id']))
        getobj1=video_sub.objects.get(video_main_id=getobj,date1=datetime.now().strftime('%Y-%m-%d'))
        return True,getobj.pk,getobj1.pk
    except:
        obj=video_main(video_name=name,category=category,youtube_url=url1,publish_date=publish_date,analysis_status=True,user_id=users.objects.get(pk=request.session['User_Id']))
        obj.save()
        obj1=video_sub(video_main_id=obj,date1=datetime.now().strftime('%Y-%m-%d'),view=int(view_count[0]),likes=int(like_count[0]),dislikes=int(dislike_count[0]))
        obj1.save()
        return True,obj.pk,obj1.pk
	#print("\n",k,"\n",v,"\n")
	
#    print(data)