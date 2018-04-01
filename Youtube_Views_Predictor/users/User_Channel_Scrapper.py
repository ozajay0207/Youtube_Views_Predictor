import pandas as pd
import numpy as np
import pickle
import requests
import random
from datetime import datetime

from users.models import user_channel_main, user_channel_sub, users
import users.find_by_channel_id as fid
API_KEYS = ["AIzaSyAgzszK84rYUM0ErWSdtiV-tyNGqGB3xFg","AIzaSyA3uNDJDl6WH0z8t9uB9pdmbIBpf54PVIE","AIzaSyCcLbOx4L6iTcS4NnvviLa1TfE7I1mnccU","AIzaSyAOpWL4ijH4vjO6sOF5ORIzohy_o2shL9s","AIzaSyCp8TYUqMn5LMgeHDvBcNcd2Y3pGbgVTAg"]
channel_data={"channelTitle":[],"ChannelDescription":[],"ChannelPublishedAt":[],"channel_videoCount":[],"channel_commentCount":[],"channel_subscriberCount":[],"channel_ViewCount":[]}
# channel_data={"social_links":[],"twitter_url":[]}
channel_dict = {}

# #print channel_data
def add_data(i,key1,key2,key3,ch_id="",channel=False):
    if not channel:
        try:
            channel_dict[ch_id][key1]=i[key2][key3]
        except:
            channel_dict[ch_id][key1] = None
    else:
        try:
            channel_data[key1].append(channel_dict[key2][key3])
            #print(len(channel_data["twitter_url"]))
            #print(len(channel_data["social_links"]))
        except:
            pass

def get_url_list(new_lst_len,lst):
    url_list=[]
    r = (new_lst_len - (new_lst_len)%50)+1
    for j in range(0,r,50):
        if j==r-1:
            v_id = ",".join(lst[j:])
        else:
            v_id = ",".join(lst[j+0:j+50])
        k = random.randint(0,4)
        API_KEY = API_KEYS[k]
        url = "https://www.googleapis.com/youtube/v3/channels?part=snippet,statistics&id="+v_id+"&key="+API_KEY
        url_list.append(url)
    return url_list


def get_channel_details(lst,name,type,url1,request):
    print('in')
    new_lst_len = len(lst)
    url_list = get_url_list(new_lst_len,lst)
    #print("url list length",len(url_list))

    c=0
    for urls in url_list:
        #print(c)
        # #print(urls)
        k = random.randint(0,4)
        API_KEY = API_KEYS[k]
        url = "https://www.googleapis.com/youtube/v3/channels?part=snippet,statistics&id="+urls+"&key="+API_KEY

        r = requests.get(urls)
        get_json = r.json()

        for i in get_json["items"]:
            channel_dict[i["id"]]={}
            add_data(i,key1="channelTitle",key2="snippet",key3="title",ch_id = i["id"])
            add_data(i,key1="ChannelDescription",key2="snippet",key3="description",ch_id=i["id"])
            add_data(i,key1="ChannelPublishedAt",key2="snippet",key3="publishedAt",ch_id=i["id"])

            add_data(i,key1="channel_ViewCount",key2="statistics",key3="viewCount",ch_id=i["id"])
            add_data(i,key1="channel_commentCount",key2="statistics",key3="commentCount",ch_id=i["id"])
            add_data(i,key1="channel_subscriberCount",key2="statistics",key3="subscriberCount",ch_id=i["id"])
            add_data(i,key1="channel_videoCount",key2="statistics",key3="videoCount",ch_id=i["id"])

        #publish_date=channel_dict['ChannelPublishedAt']
        #view_count=channel_dict['channel_ViewCount']
        #subscriber_count=channel_dict['channel_subscriberCount']
        #date1=datetime.now().strftime('%Y-%m-%d')

        dd=channel_dict[str(url1[url1.rfind('/') + 1:])]
        channel_name=dd['channelTitle']
        obj=user_channel_main(channel_name=channel_name,category='',channel_url=url1,channel_image_url='',analysis_status=True,user_id=users.objects.get(pk=request.session['User_Id']))
        obj.save()
        url1=str(url1[url1.rfind('/') + 1:])
        print(url1)
        print(obj.pk)
        fid.get_block(str(url1), obj.pk)

        #obj1=user_channel_sub(channel_id=obj,date1=date1,view_count=view_count,subscriber_count=subscriber_count)
        #obj1.save()

        #print(channel_dict)
        #for key in channel_dict:
        #    print(key)
        #    print(channel_dict[key])
        c+=1
