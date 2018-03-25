from django.shortcuts import render
from numpy import *
from datetime import datetime
from datetime import timedelta
# Create your views here.
from channel.models import channel_main, channel_sub
from users.models import users


def channel(request):
    channels_list=channel_main.objects.all()
    if 'User_Id' in request.session:
        user1 = users.objects.get(pk=request.session['User_Id'])
        User_Detail = user1
        return render(request, 'channel/all_channels.html',{'User_Detail':User_Detail,'Channel_List':channels_list})
    else:
        return render(request, 'channel/all_channels.html', {'User_Detail': '','Channel_List':channels_list})

def dashboard(request,channel_id):
    channel_main_data=channel_main.objects.get(pk=channel_id)
    channel_sub_data=channel_sub.objects.filter(channel_id = channel_main.objects.get(pk = channel_id)).order_by('-date1')
    channel_sub_data1 = channel_sub.objects.filter(channel_id=channel_main.objects.get(pk=channel_id))

    views = []
    subs = []
    dates = []
    increase_in_views=[0]
    increase_in_subs = [0]
    count_1=0
    for k in channel_sub_data1:
        if count_1 == 0:
            views.append(k.view_count)
            subs.append(k.subscriber_count)
            dates.append(k.date1)
        else:
            increase_in_views.append(k.view_count - views[count_1-1])
            increase_in_subs.append(k.subscriber_count - subs[count_1-1])
            views.append(k.view_count)
            subs.append(k.subscriber_count)
            dates.append(k.date1)
        count_1 = count_1 + 1


    increase_in_views=increase_in_views[::-1]
    increase_in_views=increase_in_views[:7]
    increase_in_subs=increase_in_subs[::-1]
    increase_in_subs=increase_in_subs[:7]
    views_for_table=[]
    subs_for_table=[]
    for c in channel_sub_data:
        views_for_table.append(c)
        subs_for_table.append(c)

    dates = dates[::-1]
    dates = dates[:7]
    dates = dates[::-1]


    #json_list = simplejson.dumps(YOUR_LIST)
    if 'User_Id' in request.session:
        user1 = users.objects.get(pk=request.session['User_Id'])
        User_Detail = user1
        return render(request, 'channel/Channel_Dashboard.html',{'User_Detail':User_Detail,'Channel_Main_Data':channel_main_data,'Channel_Sub_Data':channel_sub_data,'views':increase_in_views[::-1],'subs':increase_in_subs[::-1],'dates':dates,'table_view_increase':zip(views_for_table,increase_in_views),'table_sub_increase':zip(subs_for_table,increase_in_subs)})
    else:
        return render(request, 'channel/Channel_Dashboard.html', {'User_Detail': '','Channel_Main_Data':channel_main_data,'Channel_Sub_Data':channel_sub_data,'views':increase_in_views[::-1],'subs':increase_in_subs[::-1],'dates':dates,'table_view_increase':zip(views_for_table,increase_in_views),'table_sub_increase':zip(subs_for_table,increase_in_subs)})

def views_analysis(request,channel_id):
    channel_main_data = channel_main.objects.get(pk=channel_id)
    channel_sub_data1 = channel_sub.objects.filter(channel_id=channel_main.objects.get(pk=channel_id))
    views = []
    dates = []
    increase_in_views = [0]
    count_1 = 0
    for k in channel_sub_data1:
        if count_1 == 0:
            views.append(k.view_count)
            dates.append(k.date1)
        else:
            #increase_in_views.append(k.view_count - views[count_1 - 1])
            views.append(k.view_count)
            dates.append(k.date1)
        count_1 = count_1 + 1

    #increase_in_views = increase_in_views[::-1]
    #increase_in_views = increase_in_views[:7]
    #dates = dates[::-1]
    #dates = dates[:7]
    #dates = dates[::-1]

    #prediction
    V1=views[:len(views)-1]
    X1 = []
    for i in range(len(V1)):
        X1.append(i)

    p1 = polyfit(X1, V1, 1)
    p2 = polyfit(X1, V1, 2)

    actual=views[-1]
    predicted_p1= p1[0] * len(views) + p1[1]
    predicted_p2= p2[0] * len(views)**2 + p2[1] * len(views) + p2[2]

    predicted_views=[]
    best=[]
    if abs((predicted_p1-actual)/actual) > abs((predicted_p2-actual)/actual):
        for i in range(len(views)):
            predicted_views.append(p2[0] * i**2 + p2[1] * i + p2[2])
            best.append("p2")
    else:
        for i in range(len(views)):
            predicted_views.append(p1[0] * i + p1[1])
            best.append("p1")

    #prediction for next 30 days
    predicted_for_next_30=[]
    for i in range(len(views)+1,len(views)+31,1):
        if best[0] == "p1":
            predicted_for_next_30.append(p1[0] * i + p1[1])
        else:
            predicted_for_next_30.append(p2[0] * i ** 2 + p2[1] * i + p2[2])
    predicted_dates=[]
    for i in range(30):
        if i == 0:
            d = datetime.strptime(dates[-1], "%Y-%m-%d")
            y = d + timedelta(days=1)
            predicted_dates.append(y.strftime("%Y-%m-%d"))
        else:
            d = datetime.strptime(predicted_dates[-1], "%Y-%m-%d")
            y = d + timedelta(days=1)
            predicted_dates.append(y.strftime("%Y-%m-%d"))

    #print(len(predicted_dates),len(predicted_for_next_30))
    #for i,j in zip(views,predicted_views):
    #    print(i,j)
    if 'User_Id' in request.session:
        user1 = users.objects.get(pk=request.session['User_Id'])
        User_Detail = user1
        return render(request,'channel/views_analysis.html',{'User_Detail':User_Detail,'Channel_Main_Data':channel_main_data,'views':views,'predicted_views':predicted_views,'dates':dates,'count_1':count_1,'predicted_for_next_30':predicted_for_next_30,'predicted_dates':predicted_dates})
    else:
        return render(request, 'channel/views_analysis.html', {'User_Detail': '','Channel_Main_Data': channel_main_data,'views':views,'predicted_views':predicted_views,'dates':dates,'count_1':int(count_1),'predicted_for_next_30':predicted_for_next_30,'predicted_dates':predicted_dates})