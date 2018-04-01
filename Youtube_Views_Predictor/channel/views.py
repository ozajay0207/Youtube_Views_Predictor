from django.shortcuts import render
from numpy import *
from datetime import datetime
from datetime import timedelta
# Create your views here.
from channel.models import channel_main, channel_sub
from users.models import users


def channel(request):
    channels_list = channel_main.objects.all().order_by('pk')
    if 'User_Id' in request.session:
        user1 = users.objects.get(pk=request.session['User_Id'])
        User_Detail = user1
        return render(request, 'channel/all_channels.html', {'User_Detail': User_Detail, 'Channel_List': channels_list})
    else:
        return render(request, 'channel/all_channels.html', {'User_Detail': '', 'Channel_List': channels_list})


def dashboard(request, channel_id):
    channel_main_data = channel_main.objects.get(pk=channel_id)
    channel_sub_data = channel_sub.objects.filter(channel_id=channel_main.objects.get(pk=channel_id)).order_by('-date1')
    channel_sub_data1 = channel_sub.objects.filter(channel_id=channel_main.objects.get(pk=channel_id))

    views = []
    subs = []
    dates = []
    increase_in_views = [0]
    increase_in_subs = [0]
    count_1 = 0
    for k in channel_sub_data1:
        if count_1 == 0:
            views.append(k.view_count)
            subs.append(k.subscriber_count)
            dates.append(k.date1)
        else:
            increase_in_views.append(k.view_count - views[count_1 - 1])
            increase_in_subs.append(k.subscriber_count - subs[count_1 - 1])
            views.append(k.view_count)
            subs.append(k.subscriber_count)
            dates.append(k.date1)
        count_1 = count_1 + 1

    increase_in_views = increase_in_views[::-1]
    increase_in_views = increase_in_views[:7]
    increase_in_subs = increase_in_subs[::-1]
    increase_in_subs = increase_in_subs[:7]
    views_for_table = []
    subs_for_table = []
    for c in channel_sub_data:
        views_for_table.append(c)
        subs_for_table.append(c)

    dates = dates[::-1]
    dates = dates[:7]
    dates = dates[::-1]

    # json_list = simplejson.dumps(YOUR_LIST)
    if 'User_Id' in request.session:
        user1 = users.objects.get(pk=request.session['User_Id'])
        User_Detail = user1
        return render(request, 'channel/Channel_Dashboard.html',
                      {'User_Detail': User_Detail, 'Channel_Main_Data': channel_main_data,
                       'Channel_Sub_Data': channel_sub_data, 'views': increase_in_views[::-1],
                       'subs': increase_in_subs[::-1], 'dates': dates,
                       'table_view_increase': zip(views_for_table, increase_in_views),
                       'table_sub_increase': zip(subs_for_table, increase_in_subs)})
    else:
        return render(request, 'channel/Channel_Dashboard.html',
                      {'User_Detail': '', 'Channel_Main_Data': channel_main_data, 'Channel_Sub_Data': channel_sub_data,
                       'views': increase_in_views[::-1], 'subs': increase_in_subs[::-1], 'dates': dates,
                       'table_view_increase': zip(views_for_table, increase_in_views),
                       'table_sub_increase': zip(subs_for_table, increase_in_subs)})


def total_analysis(request, channel_id):
    channel_main_data = channel_main.objects.get(pk=channel_id)
    channel_sub_data = channel_sub.objects.filter(channel_id=channel_main.objects.get(pk=channel_id)).order_by('-date1')
    channel_sub_data1 = channel_sub.objects.filter(channel_id=channel_main.objects.get(pk=channel_id)).order_by('date1')
    old_dates = []
    old_views = []
    increse_in_old_views = [0]
    count_1 = 0
    for k in channel_sub_data1:
        if count_1 == 0:
            old_views.append(k.view_count)
            old_dates.append(k.date1)
        else:
            increse_in_old_views.append(k.view_count - old_views[count_1 - 1])
            old_views.append(k.view_count)
            old_dates.append(k.date1)
        count_1 = count_1 + 1
    print(increse_in_old_views)

    # prediction for all available old views
    V1 = old_views[:len(old_views) - 1]
    X1 = []
    for i in range(len(V1)):
        X1.append(i)
    p1 = polyfit(X1, V1, 1)
    p2 = polyfit(X1, V1, 2)
    actual = old_views[-1]
    predicted_p1 = p1[0] * len(old_views) + p1[1]
    predicted_p2 = p2[0] * len(old_views) ** 2 + p2[1] * len(old_views) + p2[2]
    predicted_old_views = []
    best = []
    if abs((predicted_p1 - actual) / actual) > abs((predicted_p2 - actual) / actual):
        for i in range(len(old_views)):
            predicted_old_views.append(p2[0] * i ** 2 + p2[1] * i + p2[2])
            best.append("p2")
    else:
        for i in range(len(old_views)):
            predicted_old_views.append(p1[0] * i + p1[1])
            best.append("p1")

    # old views,old_views_increment,prediction_old,accuracy
    accuracy_in_old_views = []
    for i in range(len(old_views)):
        accuracy_in_old_views.append(100 - abs((predicted_old_views[i] - old_views[i]) / old_views[i]))

    # prediction for next 30 days
    predicted_for_next_30 = []
    for i in range(len(old_views) + 1, len(old_views) + 31, 1):
        if best[0] == "p1":
            predicted_for_next_30.append(p1[0] * i + p1[1])
        else:
            predicted_for_next_30.append(p2[0] * i ** 2 + p2[1] * i + p2[2])
    predicted_dates = []
    for i in range(30):
        if i == 0:
            d = datetime.strptime(old_dates[-1], "%Y-%m-%d")
            y = d + timedelta(days=1)
            predicted_dates.append(y.strftime("%Y-%m-%d"))
        else:
            d = datetime.strptime(predicted_dates[-1], "%Y-%m-%d")
            y = d + timedelta(days=1)
            predicted_dates.append(y.strftime("%Y-%m-%d"))

    increase_in_predicted_views = int(predicted_for_next_30[1] - predicted_for_next_30[0])

    # print(len(predicted_dates),len(predicted_for_next_30))
    # for i,j in zip(views,predicted_old_views):
    #    print(i,j)

    old_views1 = old_views
    increse_in_old_views1 = increse_in_old_views
    predicted_old_views1 = predicted_old_views
    old_dates1 = old_dates
    accuracy_in_old_views1 = accuracy_in_old_views
    print(accuracy_in_old_views1)
    old_views1 = old_views1[::-1]
    increse_in_old_views1 = increse_in_old_views1[::-1]
    predicted_old_views1 = predicted_old_views1[::-1]
    old_dates1 = old_dates1[::-1]
    accuracy_in_old_views1 = accuracy_in_old_views1[::-1]
    avg_accuracy = average(accuracy_in_old_views)
    print('%.5f' % (avg_accuracy))

    if 'User_Id' in request.session:
        user1 = users.objects.get(pk=request.session['User_Id'])
        User_Detail = user1
        return render(request, 'channel/views_analysis.html',
                      {'User_Detail': User_Detail, 'Channel_Main_Data': channel_main_data, 'old_views': old_views,
                       'predicted_old_views': predicted_old_views, 'old_dates': old_dates, 'count_1': count_1,
                       'predicted_for_next_30': predicted_for_next_30, 'predicted_dates': predicted_dates,
                       'increse_in_old_views': increse_in_old_views,
                       'increase_in_predicted_views': increase_in_predicted_views,
                       'table_old_views': zip(old_dates1, old_views1, increse_in_old_views1, predicted_old_views1,
                                              accuracy_in_old_views1),
                       'avg_accuracy': avg_accuracy,
                       'Channel_Sub_Data': channel_sub_data,
                       'type': 'Total',
                       'label1': 'Increments in Views', 'label2': 'Prediction of Daily Views Increase For Next 30 Days',
                       'label3': 'Accuracy On Previous Data Available',
                       'label4': 'Total Views for of Previous Data Available',
                       'label5': 'Predicted Views for Next 30 Days', 'label6': 'History of Previous Predictions'})
    else:
        return render(request, 'channel/views_analysis.html',
                      {'User_Detail': '', 'Channel_Main_Data': channel_main_data, 'old_views': old_views,
                       'predicted_old_views': predicted_old_views, 'old_dates': old_dates, 'count_1': int(count_1),
                       'predicted_for_next_30': predicted_for_next_30, 'predicted_dates': predicted_dates,
                       'increse_in_old_views': increse_in_old_views,
                       'increase_in_predicted_views': increase_in_predicted_views,
                       'table_old_views': zip(old_dates1, old_views1, increse_in_old_views1, predicted_old_views1,
                                              accuracy_in_old_views1),
                       'avg_accuracy': avg_accuracy,
                       'Channel_Sub_Data': channel_sub_data,
                       'type': 'Total',
                       'label1': 'Increments in Views',
                       'label2': 'Prediction of Daily Views Increase For Next 30 Days',
                       'label3': 'Accuracy On Previous Data Available',
                       'label4': 'Total Views for of Previous Data Available',
                       'label5': 'Predicted Views for Next 30 Days',
                       'label6': 'History of Previous Predictions'})


def monthly_analysis(request, channel_id):
    channel_main_data = channel_main.objects.get(pk=channel_id)
    channel_sub_data = channel_sub.objects.filter(channel_id=channel_main.objects.get(pk=channel_id)).order_by('-date1')
    channel_sub_data1 = channel_sub.objects.filter(channel_id=channel_main.objects.get(pk=channel_id)).order_by('date1')
    channel_sub_data1 = channel_sub_data1[len(channel_sub_data1) - 30:]
    print(len(channel_sub_data1))
    old_dates = []
    old_views = []
    increse_in_old_views = [0]
    count_1 = 0
    for k in channel_sub_data1:
        if count_1 == 0:
            old_views.append(k.view_count)
            old_dates.append(k.date1)
        else:
            increse_in_old_views.append(k.view_count - old_views[count_1 - 1])
            old_views.append(k.view_count)
            old_dates.append(k.date1)
        count_1 = count_1 + 1
    print(increse_in_old_views)

    # prediction for all available old views
    V1 = old_views[:len(old_views) - 1]
    X1 = []
    for i in range(len(V1)):
        X1.append(i)
    p1 = polyfit(X1, V1, 1)
    p2 = polyfit(X1, V1, 2)
    actual = old_views[-1]
    predicted_p1 = p1[0] * len(old_views) + p1[1]
    predicted_p2 = p2[0] * len(old_views) ** 2 + p2[1] * len(old_views) + p2[2]
    predicted_old_views = []
    best = []
    if abs((predicted_p1 - actual) / actual) > abs((predicted_p2 - actual) / actual):
        for i in range(len(old_views)):
            predicted_old_views.append(p2[0] * i ** 2 + p2[1] * i + p2[2])
            best.append("p2")
    else:
        for i in range(len(old_views)):
            predicted_old_views.append(p1[0] * i + p1[1])
            best.append("p1")

    # old views,old_views_increment,prediction_old,accuracy
    accuracy_in_old_views = []
    for i in range(len(old_views)):
        accuracy_in_old_views.append(100 - abs((predicted_old_views[i] - old_views[i]) / old_views[i]))

    # prediction for next 30 days
    predicted_for_next_30 = []
    for i in range(len(old_views) + 1, len(old_views) + 31, 1):
        if best[0] == "p1":
            predicted_for_next_30.append(p1[0] * i + p1[1])
        else:
            predicted_for_next_30.append(p2[0] * i ** 2 + p2[1] * i + p2[2])
    predicted_dates = []
    for i in range(30):
        if i == 0:
            d = datetime.strptime(old_dates[-1], "%Y-%m-%d")
            y = d + timedelta(days=1)
            predicted_dates.append(y.strftime("%Y-%m-%d"))
        else:
            d = datetime.strptime(predicted_dates[-1], "%Y-%m-%d")
            y = d + timedelta(days=1)
            predicted_dates.append(y.strftime("%Y-%m-%d"))

    increase_in_predicted_views = int(predicted_for_next_30[1] - predicted_for_next_30[0])

    # print(len(predicted_dates),len(predicted_for_next_30))
    # for i,j in zip(views,predicted_old_views):
    #    print(i,j)

    old_views1 = old_views
    increse_in_old_views1 = increse_in_old_views
    predicted_old_views1 = predicted_old_views
    old_dates1 = old_dates
    accuracy_in_old_views1 = accuracy_in_old_views
    print(accuracy_in_old_views1)
    old_views1 = old_views1[::-1]
    increse_in_old_views1 = increse_in_old_views1[::-1]
    predicted_old_views1 = predicted_old_views1[::-1]
    old_dates1 = old_dates1[::-1]
    accuracy_in_old_views1 = accuracy_in_old_views1[::-1]
    avg_accuracy = average(accuracy_in_old_views)
    print('%.5f' % (avg_accuracy))

    if 'User_Id' in request.session:
        user1 = users.objects.get(pk=request.session['User_Id'])
        User_Detail = user1
        return render(request, 'channel/views_analysis.html',
                      {'User_Detail': User_Detail, 'Channel_Main_Data': channel_main_data, 'old_views': old_views,
                       'predicted_old_views': predicted_old_views, 'old_dates': old_dates, 'count_1': count_1,
                       'predicted_for_next_30': predicted_for_next_30, 'predicted_dates': predicted_dates,
                       'increse_in_old_views': increse_in_old_views,
                       'increase_in_predicted_views': increase_in_predicted_views,
                       'table_old_views': zip(old_dates1, old_views1, increse_in_old_views1, predicted_old_views1,
                                              accuracy_in_old_views1),
                       'avg_accuracy': avg_accuracy,
                       'Channel_Sub_Data': channel_sub_data,
                       'type': 'Monthly',
                       'label1': 'Increments in Views For Last 30 Days',
                       'label2': 'Prediction of Daily Views Increase For Next 30 Days',
                       'label3': 'Accuracy On Last 30 Days Data Available',
                       'label4': 'Total Views for Last 30 Days Data Available',
                       'label5': 'Predicted Views for Next 30 Days', 'label6': 'History of Last 30 Days Predictions'})
    else:
        return render(request, 'channel/views_analysis.html',
                      {'User_Detail': '', 'Channel_Main_Data': channel_main_data, 'old_views': old_views,
                       'predicted_old_views': predicted_old_views, 'old_dates': old_dates, 'count_1': int(count_1),
                       'predicted_for_next_30': predicted_for_next_30, 'predicted_dates': predicted_dates,
                       'increse_in_old_views': increse_in_old_views,
                       'increase_in_predicted_views': increase_in_predicted_views,
                       'table_old_views': zip(old_dates1, old_views1, increse_in_old_views1, predicted_old_views1,
                                              accuracy_in_old_views1),
                       'avg_accuracy': avg_accuracy,
                       'Channel_Sub_Data': channel_sub_data,
                       'type': 'Monthly',
                       'label1': 'Increments in Views For Last 30 Days',
                       'label2': 'Prediction of Daily Views Increase For Next 30 Days',
                       'label3': 'Accuracy On Last 30 Days Data Available',
                       'label4': 'Total Views for Last 30 Days Data Available',
                       'label5': 'Predicted Views for Next 30 Days', 'label6': 'History of Last 30 Days Predictions'})


def bimonthly_analysis(request, channel_id):
    channel_main_data = channel_main.objects.get(pk=channel_id)
    channel_sub_data = channel_sub.objects.filter(channel_id=channel_main.objects.get(pk=channel_id)).order_by('-date1')
    channel_sub_data1 = channel_sub.objects.filter(channel_id=channel_main.objects.get(pk=channel_id)).order_by('date1')
    channel_sub_data1 = channel_sub_data1[len(channel_sub_data1) - 15:]
    print(len(channel_sub_data1))
    old_dates = []
    old_views = []
    increse_in_old_views = [0]
    count_1 = 0
    for k in channel_sub_data1:
        if count_1 == 0:
            old_views.append(k.view_count)
            old_dates.append(k.date1)
        else:
            increse_in_old_views.append(k.view_count - old_views[count_1 - 1])
            old_views.append(k.view_count)
            old_dates.append(k.date1)
        count_1 = count_1 + 1
    print(increse_in_old_views)

    # prediction for all available old views
    V1 = old_views[:len(old_views) - 1]
    X1 = []
    for i in range(len(V1)):
        X1.append(i)
    p1 = polyfit(X1, V1, 1)
    p2 = polyfit(X1, V1, 2)
    actual = old_views[-1]
    predicted_p1 = p1[0] * len(old_views) + p1[1]
    predicted_p2 = p2[0] * len(old_views) ** 2 + p2[1] * len(old_views) + p2[2]
    predicted_old_views = []
    best = []
    if abs((predicted_p1 - actual) / actual) > abs((predicted_p2 - actual) / actual):
        for i in range(len(old_views)):
            predicted_old_views.append(p2[0] * i ** 2 + p2[1] * i + p2[2])
            best.append("p2")
    else:
        for i in range(len(old_views)):
            predicted_old_views.append(p1[0] * i + p1[1])
            best.append("p1")

    # old views,old_views_increment,prediction_old,accuracy
    accuracy_in_old_views = []
    for i in range(len(old_views)):
        accuracy_in_old_views.append(100 - abs((predicted_old_views[i] - old_views[i]) / old_views[i]))

    # prediction for next 30 days
    predicted_for_next_30 = []
    for i in range(len(old_views) + 1, len(old_views) + 16, 1):
        if best[0] == "p1":
            predicted_for_next_30.append(p1[0] * i + p1[1])
        else:
            predicted_for_next_30.append(p2[0] * i ** 2 + p2[1] * i + p2[2])
    predicted_dates = []
    for i in range(15):
        if i == 0:
            d = datetime.strptime(old_dates[-1], "%Y-%m-%d")
            y = d + timedelta(days=1)
            predicted_dates.append(y.strftime("%Y-%m-%d"))
        else:
            d = datetime.strptime(predicted_dates[-1], "%Y-%m-%d")
            y = d + timedelta(days=1)
            predicted_dates.append(y.strftime("%Y-%m-%d"))

    increase_in_predicted_views = int(predicted_for_next_30[1] - predicted_for_next_30[0])

    # print(len(predicted_dates),len(predicted_for_next_30))
    # for i,j in zip(views,predicted_old_views):
    #    print(i,j)

    old_views1 = old_views
    increse_in_old_views1 = increse_in_old_views
    predicted_old_views1 = predicted_old_views
    old_dates1 = old_dates
    accuracy_in_old_views1 = accuracy_in_old_views
    print(accuracy_in_old_views1)
    old_views1 = old_views1[::-1]
    increse_in_old_views1 = increse_in_old_views1[::-1]
    predicted_old_views1 = predicted_old_views1[::-1]
    old_dates1 = old_dates1[::-1]
    accuracy_in_old_views1 = accuracy_in_old_views1[::-1]
    avg_accuracy = average(accuracy_in_old_views)
    print('%.5f' % (avg_accuracy))

    if 'User_Id' in request.session:
        user1 = users.objects.get(pk=request.session['User_Id'])
        User_Detail = user1
        return render(request, 'channel/views_analysis.html',
                      {'User_Detail': User_Detail, 'Channel_Main_Data': channel_main_data, 'old_views': old_views,
                       'predicted_old_views': predicted_old_views, 'old_dates': old_dates, 'count_1': count_1,
                       'predicted_for_next_30': predicted_for_next_30, 'predicted_dates': predicted_dates,
                       'increse_in_old_views': increse_in_old_views,
                       'increase_in_predicted_views': increase_in_predicted_views,
                       'table_old_views': zip(old_dates1, old_views1, increse_in_old_views1, predicted_old_views1,
                                              accuracy_in_old_views1),
                       'avg_accuracy': avg_accuracy,
                       'Channel_Sub_Data': channel_sub_data,
                       'type': '15 Days',
                       'label1': 'Increments in Views For Last 15 Days',
                       'label2': 'Prediction of Daily Views Increase For Next 15 Days',
                       'label3': 'Accuracy On Last 15 Days Data Available',
                       'label4': 'Total Views for Last 15 Days Data Available',
                       'label5': 'Predicted Views for Next 15 Days', 'label6': 'History of Last 15 Days Predictions'})
    else:
        return render(request, 'channel/views_analysis.html',
                      {'User_Detail': '', 'Channel_Main_Data': channel_main_data, 'old_views': old_views,
                       'predicted_old_views': predicted_old_views, 'old_dates': old_dates, 'count_1': int(count_1),
                       'predicted_for_next_30': predicted_for_next_30, 'predicted_dates': predicted_dates,
                       'increse_in_old_views': increse_in_old_views,
                       'increase_in_predicted_views': increase_in_predicted_views,
                       'table_old_views': zip(old_dates1, old_views1, increse_in_old_views1, predicted_old_views1,
                                              accuracy_in_old_views1),
                       'avg_accuracy': avg_accuracy,
                       'Channel_Sub_Data': channel_sub_data,
                       'type': '15 Days',
                       'label1': 'Increments in Views For Last 15 Days',
                       'label2': 'Prediction of Daily Views Increase For Next 15 Days',
                       'label3': 'Accuracy On Last 15 Days Data Available',
                       'label4': 'Total Views for Last 15 Days Data Available',
                       'label5': 'Predicted Views for Next 15 Days', 'label6': 'History of Last 15 Days Predictions'})


def weekly_analysis(request, channel_id):
    channel_main_data = channel_main.objects.get(pk=channel_id)
    channel_sub_data = channel_sub.objects.filter(channel_id=channel_main.objects.get(pk=channel_id)).order_by('-date1')
    channel_sub_data1 = channel_sub.objects.filter(channel_id=channel_main.objects.get(pk=channel_id)).order_by('date1')
    channel_sub_data1 = channel_sub_data1[len(channel_sub_data1) - 7:]
    print(len(channel_sub_data1))
    old_dates = []
    old_views = []
    increse_in_old_views = [0]
    count_1 = 0
    for k in channel_sub_data1:
        if count_1 == 0:
            old_views.append(k.view_count)
            old_dates.append(k.date1)
        else:
            increse_in_old_views.append(k.view_count - old_views[count_1 - 1])
            old_views.append(k.view_count)
            old_dates.append(k.date1)
        count_1 = count_1 + 1
    print(increse_in_old_views)

    # prediction for all available old views
    V1 = old_views[:len(old_views) - 1]
    X1 = []
    for i in range(len(V1)):
        X1.append(i)
    p1 = polyfit(X1, V1, 1)
    p2 = polyfit(X1, V1, 2)
    actual = old_views[-1]
    predicted_p1 = p1[0] * len(old_views) + p1[1]
    predicted_p2 = p2[0] * len(old_views) ** 2 + p2[1] * len(old_views) + p2[2]
    predicted_old_views = []
    best = []
    if abs((predicted_p1 - actual) / actual) > abs((predicted_p2 - actual) / actual):
        for i in range(len(old_views)):
            predicted_old_views.append(p2[0] * i ** 2 + p2[1] * i + p2[2])
            best.append("p2")
    else:
        for i in range(len(old_views)):
            predicted_old_views.append(p1[0] * i + p1[1])
            best.append("p1")

    # old views,old_views_increment,prediction_old,accuracy
    accuracy_in_old_views = []
    for i in range(len(old_views)):
        accuracy_in_old_views.append(100 - abs((predicted_old_views[i] - old_views[i]) / old_views[i]))

    # prediction for next 30 days
    predicted_for_next_30 = []
    for i in range(len(old_views) + 1, len(old_views) + 8, 1):
        if best[0] == "p1":
            predicted_for_next_30.append(p1[0] * i + p1[1])
        else:
            predicted_for_next_30.append(p2[0] * i ** 2 + p2[1] * i + p2[2])
    predicted_dates = []
    for i in range(7):
        if i == 0:
            d = datetime.strptime(old_dates[-1], "%Y-%m-%d")
            y = d + timedelta(days=1)
            predicted_dates.append(y.strftime("%Y-%m-%d"))
        else:
            d = datetime.strptime(predicted_dates[-1], "%Y-%m-%d")
            y = d + timedelta(days=1)
            predicted_dates.append(y.strftime("%Y-%m-%d"))

    increase_in_predicted_views = int(predicted_for_next_30[1] - predicted_for_next_30[0])

    # print(len(predicted_dates),len(predicted_for_next_30))
    # for i,j in zip(views,predicted_old_views):
    #    print(i,j)

    old_views1 = old_views
    increse_in_old_views1 = increse_in_old_views
    predicted_old_views1 = predicted_old_views
    old_dates1 = old_dates
    accuracy_in_old_views1 = accuracy_in_old_views
    print(accuracy_in_old_views1)
    old_views1 = old_views1[::-1]
    increse_in_old_views1 = increse_in_old_views1[::-1]
    predicted_old_views1 = predicted_old_views1[::-1]
    old_dates1 = old_dates1[::-1]
    accuracy_in_old_views1 = accuracy_in_old_views1[::-1]
    avg_accuracy = average(accuracy_in_old_views)
    print('%.5f' % (avg_accuracy))

    if 'User_Id' in request.session:
        user1 = users.objects.get(pk=request.session['User_Id'])
        User_Detail = user1
        return render(request, 'channel/views_analysis.html',
                      {'User_Detail': User_Detail, 'Channel_Main_Data': channel_main_data, 'old_views': old_views,
                       'predicted_old_views': predicted_old_views, 'old_dates': old_dates, 'count_1': count_1,
                       'predicted_for_next_30': predicted_for_next_30, 'predicted_dates': predicted_dates,
                       'increse_in_old_views': increse_in_old_views,
                       'increase_in_predicted_views': increase_in_predicted_views,
                       'table_old_views': zip(old_dates1, old_views1, increse_in_old_views1, predicted_old_views1,
                                              accuracy_in_old_views1),
                       'avg_accuracy': avg_accuracy,
                       'Channel_Sub_Data': channel_sub_data,
                       'type': 'Weekly',
                       'label1': 'Increments in Views For Last Week',
                       'label2': 'Prediction of Daily Views Increase For Next Week',
                       'label3': 'Accuracy On Last Week Data Available',
                       'label4': 'Total Views for Last Week Data Available',
                       'label5': 'Predicted Views for Next Week', 'label6': 'History of Last Week Predictions'})
    else:
        return render(request, 'channel/views_analysis.html',
                      {'User_Detail': '', 'Channel_Main_Data': channel_main_data, 'old_views': old_views,
                       'predicted_old_views': predicted_old_views, 'old_dates': old_dates, 'count_1': int(count_1),
                       'predicted_for_next_30': predicted_for_next_30, 'predicted_dates': predicted_dates,
                       'increse_in_old_views': increse_in_old_views,
                       'increase_in_predicted_views': increase_in_predicted_views,
                       'table_old_views': zip(old_dates1, old_views1, increse_in_old_views1, predicted_old_views1,
                                              accuracy_in_old_views1),
                       'avg_accuracy': avg_accuracy,
                       'Channel_Sub_Data': channel_sub_data,
                       'type': 'Weekly',
                       'label1': 'Increments in Views For Last Week',
                       'label2': 'Prediction of Daily Views Increase For Next Week',
                       'label3': 'Accuracy On Last Week Data Available',
                       'label4': 'Total Views for Last Week Data Available',
                       'label5': 'Predicted Views for Next Week', 'label6': 'History of Last Week Predictions'})
