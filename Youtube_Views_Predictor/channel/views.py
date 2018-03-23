from django.shortcuts import render

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
    print(increase_in_subs)

    #json_list = simplejson.dumps(YOUR_LIST)
    if 'User_Id' in request.session:
        user1 = users.objects.get(pk=request.session['User_Id'])
        User_Detail = user1
        return render(request, 'channel/Channel_Dashboard.html',{'User_Detail':User_Detail,'Channel_Main_Data':channel_main_data,'Channel_Sub_Data':channel_sub_data,'views':increase_in_views,'subs':increase_in_subs,'dates':dates,'table_view_increase':zip(views_for_table,increase_in_views),'table_sub_increase':zip(subs_for_table,increase_in_subs)})
    else:
        return render(request, 'channel/Channel_Dashboard.html', {'User_Detail': '','Channel_Main_Data':channel_main_data,'Channel_Sub_Data':channel_sub_data,'views':increase_in_views,'subs':increase_in_subs,'dates':dates,'table_view_increase':zip(views_for_table,increase_in_views),'table_sub_increase':zip(subs_for_table,increase_in_subs)})