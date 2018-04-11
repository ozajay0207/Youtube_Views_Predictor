from datetime import datetime, timedelta

from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from users.models import users, video_main, video_sub, user_channel_main, user_channel_sub
import users.User_Video_Scraper as uvs
import users.User_Channel_Scrapper as us1
from numpy import *


# from Crypto.Hash import SHA256
# Create your views here.

def DashBoard(request):
    if 'User_Id' in request.session:
        user1 = users.objects.get(pk=request.session['User_Id'])
        User_Detail = user1
        video_main_obj = video_main.objects.filter(user_id=user1.pk)
        video_sub_obj=video_sub.objects.filter(video_main_id__in=video_main_obj).order_by("-date1","video_main_id")
        channel_main_obj = user_channel_main.objects.filter(user_id=user1.pk)
        # print(channel_main_obj)
        channel_sub_obj = user_channel_sub.objects.filter(channel_id__in=channel_main_obj).order_by("-date1","channel_id_id")
        # print(channel_sub_obj)
        channel_obj = zip(channel_main_obj, channel_sub_obj)
        video_obj=zip(video_main_obj,video_sub_obj)
        return render(request, 'users/Users_Dashboard.html',
                      {'User_Detail': User_Detail, 'video_details': video_main_obj, 'channel_details': channel_obj,'video_details':video_obj})
    else:
        return HttpResponseRedirect('/Home/')

def Sign_Up(request):
    if 'User_Id' in request.session:
        user1 = users.objects.get(pk=request.session['User_Id'])
        User_Detail = user1
        return render(request, 'users/Users_Dashboard.html', {'User_Detail': User_Detail, })
    else:
        if request.method == 'POST':
            Email = request.POST.get('val-email1')
            Display_Name = request.POST.get('val-display-name')
            Password = request.POST.get('val-password1')
            #           Password_Hash=SHA256.new(Password.encode('utf-8')).hexdigest()
            user1 = users(Email=Email, Display_Name=Display_Name, Password=Password)
            user1.save()
            request.session['User_Id'] = user1.id

            return HttpResponseRedirect('/users/')
            # User_Detail=user1
            # return render(request, 'users/Users_Dashboard.html', {'User_Detail':User_Detail})
        else:
            return HttpResponseRedirect('/Home/')

def Sign_In(request):
    if 'User_Id' in request.session:
        return HttpResponseRedirect('/users/')
        # user1 = users.objects.get(pk=request.session['User_Id'])
        # User_Detail = user1
        # return render(request, 'users/Users_Dashboard.html', {'User_Detail':User_Detail})
    else:
        if request.method == 'POST':
            Email = request.POST.get('val-email')
            Password = request.POST.get('val-password')
            #           Password_Hash = SHA256.new(Password.encode('utf-8')).hexdigest()
            try:
                user1 = users.objects.get(Email=Email, Password=Password)
                request.session['User_Id'] = user1.id
                return HttpResponseRedirect('/users/')
                # User_Detail = user1
                # return render(request, 'users/Users_Dashboard.html', {'User_Detail': User_Detail})
            except:
                return HttpResponseRedirect('/Home/')
        else:
            return HttpResponseRedirect('/Home/')

def Sign_Out(request):
    del request.session['User_Id']
    return HttpResponseRedirect('/Home/')

def login(request):
    return render(request, 'users/Login.html')

def register(request):
    return render(request, 'users/Register.html')

def validate_email(request):
    print("validate")
    Email = request.GET.get("username")
    test = users.objects.filter(Email=Email).exists()
    print(test)
    if test:
        obj = users.objects.get(Email=Email)
        print(obj.Password)

    data = {
        'is_taken': users.objects.filter(Email=Email).exists()
    }
    if not data['is_taken']:
        data['error_message'] = "no such user"
    else:
        data['pass'] = obj.Password
    return JsonResponse(data)

def validate_display_name(request):
    if request.method == "POST":
        query = request.POST.get('val-display-name')
        # print(query)
        if query == '':
            return render(request, 'users/search_result.html', {'data': 'None'})
        else:
            data = users.objects.get(Display_Name=query)
    else:
        query = ''
        data = {}

    return render(request, 'users/search_result.html', {'data': data})

@csrf_exempt
def get_data(request):
    if request.method == "POST":
        url = request.POST.get("search")
        name = request.POST.get("name")
        type = request.POST.get("type")
        if type == "Video":
            final_url = url[url.rfind('=') + 1:]
            f, mainid, subid = uvs.get_video_details([final_url], name, type, url, request)

            if f == True:
                user1 = users.objects.get(pk=request.session['User_Id'])
                User_Detail = user1
                uvmain = video_main.objects.get(user_id=user1.pk, id=mainid)
                uvsub = video_sub.objects.filter(video_main_id=video_main.objects.get(id=uvmain.id)).order_by('-date1')
                dates = []
                views = []
                likes = []
                dislikes = []
                for i in uvsub:
                    dates.append(i.date1)
                    views.append(i.view)
                    likes.append(i.likes)
                    dislikes.append(i.dislikes)
                return render(request, 'users/less_than_7_days.html', {'User_Detail': User_Detail,
                                                                       'status': 'We are currently analysing your Video....We will notify you on your email after ' + str(
                                                                           8 - len(uvsub)) + ' days',
                                                                       'uvmain': uvmain, 'uvsub': uvsub,
                                                                       'user_view_table': zip(dates, views, likes,
                                                                                              dislikes)})

        else:
            final_url = url
            flag, obj, obj1 = us1.get_channel_details([final_url], request)
            ucmain = user_channel_main.objects.get(pk=obj)
            ucsub = user_channel_sub.objects.filter(pk=obj1)
            user1 = users.objects.get(pk=request.session['User_Id'])
            User_Detail = user1
            dates = []
            views = []
            subscribers = []
            for i in ucsub:
                dates.append(i.date1)
                views.append(i.view_count)
                subscribers.append(i.subscriber_count)
            if flag:
                return render(request, 'users/less_than_7_days_channel.html', {'User_Detail': User_Detail,
                                                                               'status': 'We are currently analysing your Video....We will notify you on your email after ' + str(
                                                                                   8 - len(ucsub)) + ' days',
                                                                               'ucmain': ucmain, 'ucsub': ucsub,
                                                                               'user_view_table': zip(dates, views,
                                                                                                      subscribers, )})

            else:
                return HttpResponseRedirect(reverse(DashBoard))
    else:
        return HttpResponseRedirect(reverse(DashBoard))


def total_view_video_analysis(request, video_id):
    if 'User_Id' in request.session:
        user1 = users.objects.get(pk=request.session['User_Id'])
        User_Detail = user1
        uvmain = video_main.objects.get(user_id=user1.pk, id=video_id)
        uvsub = video_sub.objects.filter(video_main_id=video_main.objects.get(id=uvmain.id)).order_by('-date1')
        if len(uvsub) > 7:
            # print('inside123')
            channel_main_data = video_main.objects.get(user_id=user1.pk, id=uvmain.id)
            channel_sub_data = video_sub.objects.filter(
                video_main_id=video_main.objects.get(id=uvmain.id)).order_by('-date1')
            channel_sub_data1 = video_sub.objects.filter(
                video_main_id=video_main.objects.get(id=uvmain.id)).order_by('date1')

            c1 = channel_sub_data1
            try:
                if (len(uvsub) > 25):
                    channel_sub_data1 = channel_sub_data1[10:]
                else:
                    pass
            except:
                pass
            # print(len(channel_sub_data1))
            old_dates = []
            old_views = []
            increse_in_old_views = [0]
            count_1 = 0
            for k in channel_sub_data1:
                if count_1 == 0:
                    old_views.append(k.view)
                    old_dates.append(k.date1)
                else:
                    increse_in_old_views.append(k.view - old_views[count_1 - 1])
                    old_views.append(k.view)
                    old_dates.append(k.date1)
                count_1 = count_1 + 1
                ##print(increse_in_old_views)

                # prediction for all available old views
            V1 = old_views[:len(old_views) - 1]
            X1 = []
            for i in range(len(V1)):
                X1.append(i)
            actual = old_views[-1]
            p1 = polyfit(X1, V1, 1)
            p2 = polyfit(X1, V1, 2)
            p3 = polyfit(X1, V1, 3)

            predicted_p1 = p1[0] * len(uvsub) + p1[1]
            predicted_p2 = p2[0] * len(uvsub) ** 2 + p2[1] * len(uvsub) + p2[2]
            predicted_p3 = p3[0] * len(uvsub) ** 3 + p3[1] * len(uvsub) ** 2 + p3[2] * len(uvsub) + p3[3]

            accuracy_p1 = 100 - abs((predicted_p1 - actual) / actual) * 100
            accuracy_p2 = 100 - abs((predicted_p2 - actual) / actual) * 100
            accuracy_p3 = 100 - abs((predicted_p3 - actual) / actual) * 100
            accuracies = {'p1': accuracy_p1, 'p2': accuracy_p2, 'p3': accuracy_p3}
            ##print(accuracy_p1,accuracy_p2,accuracy_p3,accuracy_p4,accuracy_p5)
            best = []
            predicted_old_views = []
            if accuracy_p1 > accuracy_p2 and accuracy_p1 > accuracy_p3:
                for i in range(len(old_views)):
                    predicted_old_views.append(p1[0] * i + p1[1])
                avg_accuracy = float(100 - abs((predicted_p1 - actual) / actual) * 100)
                best.append("p1")
            elif accuracy_p2 > accuracy_p1 and accuracy_p2 > accuracy_p3:
                for i in range(len(old_views)):
                    predicted_old_views.append(p2[0] * i ** 2 + p2[1] * i + p2[2])
                avg_accuracy = float(100 - abs((predicted_p2 - actual) / actual) * 100)
                best.append("p2")
            elif accuracy_p3 > accuracy_p1 and accuracy_p3 > accuracy_p2:
                for i in range(len(old_views)):
                    predicted_old_views.append(p3[0] * i ** 3 + p3[1] * i ** 2 + p3[2] * i + p3[3])
                avg_accuracy = float(100 - abs((predicted_p3 - actual) / actual) * 100)
                best.append("p3")

            # old views,old_views_increment,prediction_old,accuracy
            accuracy_in_old_views = []
            for i in range(len(old_views)):
                accuracy_in_old_views.append(
                    100 - abs((predicted_old_views[i] - old_views[i]) / old_views[i]))

                # prediction for next 30 days
            predicted_for_next_30 = []
            if len(uvsub) > 25:
                for i in range(len(old_views) + 11, len(old_views) + 42, 1):
                    if best[0] == "p1":
                        predicted_for_next_30.append(p1[0] * i + p1[1])
                    elif best[0] == "p2":
                        predicted_for_next_30.append(p2[0] * i ** 2 + p2[1] * i + p2[2])
                    elif best[0] == "p3":
                        predicted_for_next_30.append(p3[0] * i ** 3 + p3[1] * i ** 2 + p3[2] * i + p3[3])
            else:
                for i in range(len(old_views) + 1, len(old_views) + 31, 1):
                    if best[0] == "p1":
                        predicted_for_next_30.append(p1[0] * i + p1[1])
                    elif best[0] == "p2":
                        predicted_for_next_30.append(p2[0] * i ** 2 + p2[1] * i + p2[2])
                    elif best[0] == "p3":
                        predicted_for_next_30.append(p3[0] * i ** 3 + p3[1] * i ** 2 + p3[2] * i + p3[3])

            # print('\n',p2,'\n\n')
            # print(predicted_for_next_30)
            predicted_dates = []
            for i in range(31):
                if i == 0:
                    d = datetime.strptime(old_dates[-1], "%Y-%m-%d")
                    y = d + timedelta(days=1)
                    predicted_dates.append(y.strftime("%Y-%m-%d"))
                else:
                    d = datetime.strptime(predicted_dates[-1], "%Y-%m-%d")
                    y = d + timedelta(days=1)
                    predicted_dates.append(y.strftime("%Y-%m-%d"))

            increase_in_predicted_views = int(predicted_for_next_30[1]) - int(predicted_for_next_30[0])
            print(best,increase_in_predicted_views)
            if increase_in_predicted_views < 0:
                predicted_for_next_30[:] = []
                if best[0] == 'p1':
                    best[0] = 'p2'
                    if len(uvsub) > 25:
                        for i in range(len(old_views) + 11, len(old_views) + 41, 1):
                            predicted_for_next_30.append(p2[0] * i ** 2 + p2[1] * i + p2[2])
                    else:
                        for i in range(len(old_views) + 1, len(old_views) + 31, 1):
                            predicted_for_next_30.append(p2[0] * i ** 2 + p2[1] * i + p2[2])
                    increase_in_predicted_views = int(predicted_for_next_30[1]) - int(predicted_for_next_30[0])
                    avg_accuracy = float(100 - abs((predicted_p2 - actual) / actual) * 100)
                    if increase_in_predicted_views < 0:
                        best[0] = 'p3'
                        predicted_for_next_30[:] = []
                        for i in range(len(old_views) + 11, len(old_views) + 42, 1):
                            predicted_for_next_30.append(p3[0] * i ** 3 + p3[1] * i ** 2 + p3[2] * i + p3[3])
                        increase_in_predicted_views = int(predicted_for_next_30[1]) - int(predicted_for_next_30[0])
                        avg_accuracy = float(100 - abs((predicted_p3 - actual) / actual) * 100)
                elif best[0] == 'p2':
                    best[0] = 'p1'
                    if len(uvsub) > 25:
                        for i in range(len(old_views) + 11, len(old_views) + 41, 1):
                            predicted_for_next_30.append(p1[0] * i + p1[1])
                    else:
                        for i in range(len(old_views) + 1, len(old_views) + 31, 1):
                            predicted_for_next_30.append(p1[0] * i + p1[1])
                    increase_in_predicted_views = int(predicted_for_next_30[1]) - int(predicted_for_next_30[0])
                    avg_accuracy = float(100 - abs((predicted_p1 - actual) / actual) * 100)
                    if increase_in_predicted_views < 0:
                        best[0] = 'p3'
                        predicted_for_next_30[:] = []
                        if len(uvsub) > 25:
                            for i in range(len(old_views) + 11, len(old_views) + 41, 1):
                                predicted_for_next_30.append(p3[0] * i ** 3 + p3[1] * i ** 2 + p3[2] * i + p3[3])
                        else:
                            for i in range(len(old_views) + 1, len(old_views) + 31, 1):
                                predicted_for_next_30.append(p3[0] * i ** 3 + p3[1] * i ** 2 + p3[2] * i + p3[3])
                        increase_in_predicted_views = int(predicted_for_next_30[1]) - int(predicted_for_next_30[0])
                        avg_accuracy = float(100 - abs((predicted_p3 - actual) / actual) * 100)
                elif best[0] == 'p3':
                    best[0] = 'p2'
                    if len(uvsub) > 25:
                        for i in range(len(old_views) + 11, len(old_views) + 41, 1):
                            predicted_for_next_30.append(p2[0] * i ** 2 + p2[1] * i + p2[2])
                    else:
                        for i in range(len(old_views) + 1, len(old_views) + 31, 1):
                            predicted_for_next_30.append(p2[0] * i ** 2 + p2[1] * i + p2[2])
                    increase_in_predicted_views = int(predicted_for_next_30[1]) - int(predicted_for_next_30[0])
                    avg_accuracy = float(100 - abs((predicted_p2 - actual) / actual) * 100)
                    if increase_in_predicted_views < 0:
                        best[0] = 'p1'
                        predicted_for_next_30[:] = []
                        if len(uvsub) > 25:
                            for i in range(len(old_views) + 11, len(old_views) + 41, 1):
                                predicted_for_next_30.append(p1[0] * i + p1[1])
                        else:
                            for i in range(len(old_views) + 1, len(old_views) + 31, 1):
                                predicted_for_next_30.append(p1[0] * i + p1[1])
                        increase_in_predicted_views = int(predicted_for_next_30[1]) - int(predicted_for_next_30[0])
                        avg_accuracy = float(100 - abs((predicted_p1 - actual) / actual) * 100)
                        # elif best[0] == "p3":
                        #    predicted_for_next_30.append(p3[0] * i ** 3 + p3[1] * i ** 2 + p3[2] * i + p3[3])

            # print(increase_in_predicted_views)
            # #print(len(predicted_dates),len(predicted_for_next_30))
            # for i,j in zip(views,predicted_old_views):
            #    #print(i,j)
            # print(best)
            old_views[:] = []
            old_dates[:] = []
            increse_in_old_views[:] = []
            increse_in_old_views = [0]
            print(best)
            count_1 = 0
            for k in c1:
                if count_1 == 0:
                    old_views.append(k.view)
                    old_dates.append(k.date1)
                else:
                    increse_in_old_views.append(k.view - old_views[count_1 - 1])
                    old_views.append(k.view)
                    old_dates.append(k.date1)
                count_1 = count_1 + 1
            predicted_old_views[:] = []
            if best[0] == 'p1':
                for i in range(len(old_views)):
                    predicted_old_views.append(p1[0] * i + p1[1])
            elif best[0] == 'p2':
                for i in range(len(old_views)):
                    predicted_old_views.append(p2[0] * i ** 2 + p2[1] * i + p2[2])
            elif best[0] == 'p3':
                for i in range(len(old_views)):
                    predicted_old_views.append(p3[0] * i ** 3 + p3[1] * i ** 2 + p3[2] * i + p3[3])
            old_views1 = old_views
            increse_in_old_views1 = increse_in_old_views
            predicted_old_views1 = predicted_old_views
            old_dates1 = old_dates
            accuracy_in_old_views1 = accuracy_in_old_views
            # print(accuracy_in_old_views1)
            old_views1 = old_views1[::-1]
            increse_in_old_views1 = increse_in_old_views1[::-1]
            predicted_old_views1 = predicted_old_views1[::-1]
            old_dates1 = old_dates1[::-1]
            accuracy_in_old_views1 = accuracy_in_old_views1[::-1]
            #if best[0] == 'p1':
                #avg_accuracy = accuracies['p1']
            avg_accuracy = '%.5f' % (avg_accuracy)
            #elif best[0] == 'p2':
                #avg_accuracy = accuracies['p2']
            #    avg_accuracy = '%.5f' % (avg_accuracy)
            #else:
                #avg_accuracy = accuracies['p3']
            #    avg_accuracy = '%.5f' % (avg_accuracy)

            user1 = users.objects.get(pk=request.session['User_Id'])
            User_Detail = user1
            return render(request, 'users/user_views_analysis.html',
                          {'User_Detail': User_Detail, 'Channel_Main_Data': channel_main_data,
                           'old_views': old_views,
                           'predicted_old_views': predicted_old_views, 'old_dates': old_dates,
                           'count_1': count_1,
                           'predicted_for_next_30': predicted_for_next_30,
                           'predicted_dates': predicted_dates,
                           'increse_in_old_views': increse_in_old_views,
                           'increase_in_predicted_views': increase_in_predicted_views,
                           'table_old_views': zip(old_dates1, old_views1, increse_in_old_views1,
                                                  predicted_old_views1,
                                                  accuracy_in_old_views1),
                           'avg_accuracy': avg_accuracy,
                           'Channel_Sub_Data': channel_sub_data,
                           'type': 'Total',
                           'label1': 'Increments in Views',
                           'label2': 'Prediction of Daily Views Increase For Next 7 Days',
                           'label3': 'Accuracy On Previous Data Available',
                           'label4': 'Total Views for of Previous Data Available',
                           'label5': 'Predicted Views for Next 30 Days',
                           'label6': 'History of Previous Predictions'})
            '''
        else:
            c1 = channel_sub_data1
            # print(len(channel_sub_data1))
            old_dates = []
            old_views = []
            increse_in_old_views = [0]
            count_1 = 0
            for k in channel_sub_data1:
                if count_1 == 0:
                    old_views.append(k.view)
                    old_dates.append(k.date1)
                else:
                    increse_in_old_views.append(k.view - old_views[count_1 - 1])
                    old_views.append(k.view)
                    old_dates.append(k.date1)
                count_1 = count_1 + 1
                ##print(increse_in_old_views)

                # prediction for all available old views
            V1 = old_views[:len(old_views) - 1]
            X1 = []
            for i in range(len(V1)):
                X1.append(i)
            actual = old_views[-1]
            p1 = polyfit(X1, V1, 1)
            p2 = polyfit(X1, V1, 2)
            p3 = polyfit(X1, V1, 3)
            p4 = polyfit(X1, V1, 4)
            p5 = polyfit(X1, V1, 5)
            predicted_p1 = p1[0] * len(uvsub) + p1[1]
            predicted_p2 = p2[0] * len(uvsub) ** 2 + p2[1] * len(uvsub) + p2[2]
            predicted_p3 = p3[0] * len(uvsub) ** 3 + p3[1] * len(uvsub) ** 2 + p3[2] * len(uvsub) + p3[3]
            predicted_p4 = p4[0] * len(uvsub) ** 4 + p4[1] * len(uvsub) ** 3 + p4[2] * len(uvsub) ** 2 + p4[
                                                                                                             3] * len(
                uvsub) + p4[4]
            predicted_p5 = p5[0] * len(uvsub) ** 5 + p5[1] * len(uvsub) ** 4 + p5[2] * len(uvsub) ** 3 + p5[
                                                                                                             3] * len(
                uvsub) ** 2 + p5[4] * len(uvsub) + p5[5]
            accuracy_p1 = 100 - abs((predicted_p1 - actual) / actual) * 100
            accuracy_p2 = 100 - abs((predicted_p2 - actual) / actual) * 100
            accuracy_p3 = 100 - abs((predicted_p3 - actual) / actual) * 100
            accuracy_p4 = 100 - abs((predicted_p4 - actual) / actual) * 100
            accuracy_p5 = 100 - abs((predicted_p5 - actual) / actual) * 100
            accuracies = {'p1': accuracy_p1, 'p2': accuracy_p2, 'p3': accuracy_p3, 'p4': accuracy_p4,
                          'p5': accuracy_p5}
            ##print(accuracy_p1,accuracy_p2,accuracy_p3,accuracy_p4,accuracy_p5)
            best = []
            predicted_old_views = []
            if accuracy_p1 > accuracy_p2 and accuracy_p1 > accuracy_p3 and accuracy_p1 > accuracy_p4 and accuracy_p1 > accuracy_p5:
                for i in range(len(old_views)):
                    predicted_old_views.append(p1[0] * i + p1[1])
                best.append("p1")
            elif accuracy_p2 > accuracy_p1 and accuracy_p2 > accuracy_p3 and accuracy_p2 > accuracy_p4 and accuracy_p2 > accuracy_p5:
                for i in range(len(old_views)):
                    predicted_old_views.append(p2[0] * i ** 2 + p2[1] * i + p2[2])
                best.append("p2")
            elif accuracy_p3 > accuracy_p1 and accuracy_p3 > accuracy_p2 and accuracy_p3 > accuracy_p4 and accuracy_p3 > accuracy_p5:
                for i in range(len(old_views)):
                    predicted_old_views.append(p3[0] * i ** 3 + p3[1] * i ** 2 + p3[2] * i + p3[3])
                best.append("p3")
            elif accuracy_p4 > accuracy_p1 and accuracy_p4 > accuracy_p2 and accuracy_p4 > accuracy_p3 and accuracy_p4 > accuracy_p5:
                for i in range(len(old_views)):
                    predicted_old_views.append(p4[0] * i ** 4 + p4[1] * i ** 3 + p4[2] * i ** 2 + p4[3] * i + p4[4])
                best.append("p4")
            else:
                for i in range(len(old_views)):
                    predicted_old_views.append(
                        p5[0] * i ** 5 + p5[1] * i ** 4 + p5[2] * i ** 3 + p5[3] * i ** 2 + p5[4] * i + p5[5])
                best.append("p5")

                # old views,old_views_increment,prediction_old,accuracy
            accuracy_in_old_views = []
            for i in range(len(old_views)):
                accuracy_in_old_views.append(
                    100 - abs((predicted_old_views[i] - old_views[i]) / old_views[i]))

                # prediction for next 30 days
            predicted_for_next_30 = []
            for i in range(len(old_views) + 1, len(old_views) + 31, 1):
                if best[0] == "p1":
                    predicted_for_next_30.append(p1[0] * i + p1[1])
                elif best[0] == "p2":
                    predicted_for_next_30.append(p2[0] * i ** 2 + p2[1] * i + p2[2])
                elif best[0] == "p3":
                    predicted_for_next_30.append(p3[0] * i ** 3 + p3[1] * i ** 2 + p3[2] * i + p3[3])
                elif best[0] == "p4":
                    predicted_for_next_30.append(
                        p4[0] * i ** 4 + p4[1] * i ** 3 + p4[2] * i ** 2 + p4[3] * i + p4[4])
                else:
                    predicted_for_next_30.append(
                        p5[0] * i ** 5 + p5[1] * i ** 4 + p5[2] * i ** 3 + p5[3] * i ** 2 + p5[4] * i + p5[5])
            # print('\n',p2,'\n\n')
            # print(predicted_for_next_30)
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

            increase_in_predicted_views = int(predicted_for_next_30[1]) - int(predicted_for_next_30[0])

            # print(increase_in_predicted_views)
            # #print(len(predicted_dates),len(predicted_for_next_30))
            # for i,j in zip(views,predicted_old_views):
            #    #print(i,j)
            # print(best)
            old_views1 = old_views
            increse_in_old_views1 = increse_in_old_views
            predicted_old_views1 = predicted_old_views
            old_dates1 = old_dates
            accuracy_in_old_views1 = accuracy_in_old_views
            # print(accuracy_in_old_views1)
            old_views1 = old_views1[::-1]
            increse_in_old_views1 = increse_in_old_views1[::-1]
            predicted_old_views1 = predicted_old_views1[::-1]
            old_dates1 = old_dates1[::-1]
            accuracy_in_old_views1 = accuracy_in_old_views1[::-1]
            if best[0] == 'p1':
                avg_accuracy = accuracies['p1']
                avg_accuracy = '%.5f' % (avg_accuracy)
            elif best[0] == 'p2':
                avg_accuracy = accuracies['p2']
                avg_accuracy = '%.5f' % (avg_accuracy)
            elif best[0] == 'p3':
                avg_accuracy = accuracies['p3']
                avg_accuracy = '%.5f' % (avg_accuracy)
            elif best[0] == 'p4':
                avg_accuracy = accuracies['p4']
                avg_accuracy = '%.5f' % (avg_accuracy)
            else:
                avg_accuracy = accuracies['p5']
                avg_accuracy = '%.5f' % (avg_accuracy)
            user1 = users.objects.get(pk=request.session['User_Id'])
            User_Detail = user1
            return render(request, 'users/user_views_analysis.html',
                          {'User_Detail': User_Detail, 'Channel_Main_Data': channel_main_data,
                           'old_views': old_views,
                           'predicted_old_views': predicted_old_views, 'old_dates': old_dates,
                           'count_1': count_1,
                           'predicted_for_next_30': predicted_for_next_30,
                           'predicted_dates': predicted_dates,
                           'increse_in_old_views': increse_in_old_views,
                           'increase_in_predicted_views': increase_in_predicted_views,
                           'table_old_views': zip(old_dates1, old_views1, increse_in_old_views1,
                                                  predicted_old_views1,
                                                  accuracy_in_old_views1),
                           'avg_accuracy': avg_accuracy,
                           'Channel_Sub_Data': channel_sub_data,
                           'type': 'Total',
                           'label1': 'Increments in Views',
                           'label2': 'Prediction of Daily Views Increase For Next 7 Days',
                           'label3': 'Accuracy On Previous Data Available',
                           'label4': 'Total Views for of Previous Data Available',
                           'label5': 'Predicted Views for Next 15 Days',
                           'label6': 'History of Previous Predictions'})
        '''
        else:
            dates = []
            views = []
            likes = []
            dislikes = []
            for i in uvsub:
                dates.append(i.date1)
                views.append(i.view)
                likes.append(i.likes)
                dislikes.append(i.dislikes)
            return render(request, 'users/less_than_7_days.html', {'User_Detail': User_Detail,
                                                               'status': 'We are currently analysing your Video....We will notify you on your email after ' + str(
                                                                   8 - len(uvsub)) + ' days',
                                                               'uvmain': uvmain, 'uvsub': uvsub,
                                                               'user_view_table': zip(dates, views, likes,
                                                                                      dislikes)})

    else:
        return HttpResponseRedirect('/Home/')

def weekly_view_video_analysis(request, video_id):
    if 'User_Id' in request.session:
        user1 = users.objects.get(pk=request.session['User_Id'])
        User_Detail = user1
        uvmain = video_main.objects.get(user_id=user1.pk, id=video_id)
        uvsub = video_sub.objects.filter(video_main_id=video_main.objects.get(id=uvmain.id)).order_by('-date1')
        if len(uvsub) > 7:
            # print('inside123')
            channel_main_data = video_main.objects.get(user_id=user1.pk, id=uvmain.id)
            channel_sub_data = video_sub.objects.filter(
                video_main_id=video_main.objects.get(id=uvmain.id)).order_by('-date1')
            channel_sub_data1 = video_sub.objects.filter(
                video_main_id=video_main.objects.get(id=uvmain.id)).order_by('date1')
            channel_sub_data1 = channel_sub_data1[len(channel_sub_data1)-7:]
            c1 = channel_sub_data1

            # print(len(channel_sub_data1))
            old_dates = []
            old_views = []
            increse_in_old_views = [0]
            count_1 = 0
            for k in channel_sub_data1:
                if count_1 == 0:
                    old_views.append(k.view)
                    old_dates.append(k.date1)
                else:
                    increse_in_old_views.append(k.view - old_views[count_1 - 1])
                    old_views.append(k.view)
                    old_dates.append(k.date1)
                count_1 = count_1 + 1
                ##print(increse_in_old_views)

                # prediction for all available old views
            V1 = old_views[:len(old_views) - 1]
            X1 = []
            for i in range(len(V1)):
                X1.append(i)
            actual = old_views[-1]
            p1 = polyfit(X1, V1, 1)
            p2 = polyfit(X1, V1, 2)
            p3 = polyfit(X1, V1, 3)

            predicted_p1 = p1[0] * len(uvsub) + p1[1]
            predicted_p2 = p2[0] * len(uvsub) ** 2 + p2[1] * len(uvsub) + p2[2]
            predicted_p3 = p3[0] * len(uvsub) ** 3 + p3[1] * len(uvsub) ** 2 + p3[2] * len(uvsub) + p3[3]

            accuracy_p1 = 100 - abs((predicted_p1 - actual) / actual) * 100
            accuracy_p2 = 100 - abs((predicted_p2 - actual) / actual) * 100
            accuracy_p3 = 100 - abs((predicted_p3 - actual) / actual) * 100
            accuracies = {'p1': accuracy_p1, 'p2': accuracy_p2, 'p3': accuracy_p3}
            ##print(accuracy_p1,accuracy_p2,accuracy_p3,accuracy_p4,accuracy_p5)
            best = []
            predicted_old_views = []
            if accuracy_p1 > accuracy_p2 and accuracy_p1 > accuracy_p3:
                for i in range(len(old_views)):
                    predicted_old_views.append(p1[0] * i + p1[1])
                best.append("p1")
            elif accuracy_p2 > accuracy_p1 and accuracy_p2 > accuracy_p3:
                for i in range(len(old_views)):
                    predicted_old_views.append(p2[0] * i ** 2 + p2[1] * i + p2[2])
                best.append("p2")
            elif accuracy_p3 > accuracy_p1 and accuracy_p3 > accuracy_p2:
                for i in range(len(old_views)):
                    predicted_old_views.append(p3[0] * i ** 3 + p3[1] * i ** 2 + p3[2] * i + p3[3])
                best.append("p3")

            # old views,old_views_increment,prediction_old,accuracy
            accuracy_in_old_views = []
            for i in range(len(old_views)):
                accuracy_in_old_views.append(
                    100 - abs((predicted_old_views[i] - old_views[i]) / old_views[i]))

                # prediction for next 30 days
            predicted_for_next_30 = []
            for i in range(len(old_views) + 1, len(old_views) + 8, 1):
                if best[0] == "p1":
                    predicted_for_next_30.append(p1[0] * i + p1[1])
                elif best[0] == "p2":
                    predicted_for_next_30.append(p2[0] * i ** 2 + p2[1] * i + p2[2])
                elif best[0] == "p3":
                    predicted_for_next_30.append(p3[0] * i ** 3 + p3[1] * i ** 2 + p3[2] * i + p3[3])

            # print('\n',p2,'\n\n')
            # print(predicted_for_next_30)
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

            increase_in_predicted_views = int(predicted_for_next_30[1]) - int(predicted_for_next_30[0])
            if increase_in_predicted_views < 0:
                predicted_for_next_30[:] = []
                if best[0] == 'p1':
                    best[0] = 'p2'
                    for i in range(len(old_views) + 1, len(old_views) + 8, 1):
                        predicted_for_next_30.append(p2[0] * i ** 2 + p2[1] * i + p2[2])
                    increase_in_predicted_views = int(predicted_for_next_30[1]) - int(predicted_for_next_30[0])
                    if increase_in_predicted_views < 0:
                        best[0] = 'p3'
                        predicted_for_next_30[:] = []
                        for i in range(len(old_views) + 1, len(old_views) + 8, 1):
                            predicted_for_next_30.append(p3[0] * i ** 3 + p3[1] * i ** 2 + p3[2] * i + p3[3])
                        increase_in_predicted_views = int(predicted_for_next_30[1]) - int(predicted_for_next_30[0])
                elif best[0] == 'p2':
                    best[0] = 'p1'
                    for i in range(len(old_views) + 1, len(old_views) + 8, 1):
                        predicted_for_next_30.append(p1[0] * i + p1[1])
                    increase_in_predicted_views = int(predicted_for_next_30[1]) - int(predicted_for_next_30[0])
                    if increase_in_predicted_views < 0:
                        best[0] = 'p3'
                        predicted_for_next_30[:] = []
                        for i in range(len(old_views) + 1, len(old_views) + 8, 1):
                            predicted_for_next_30.append(p3[0] * i ** 3 + p3[1] * i ** 2 + p3[2] * i + p3[3])
                        increase_in_predicted_views = int(predicted_for_next_30[1]) - int(predicted_for_next_30[0])


                elif best[0] == 'p3':
                    best[0] = 'p2'
                    for i in range(len(old_views) + 1, len(old_views) + 8, 1):
                        predicted_for_next_30.append(p2[0] * i ** 2 + p2[1] * i + p2[2])
                    increase_in_predicted_views = int(predicted_for_next_30[1]) - int(predicted_for_next_30[0])
                    if increase_in_predicted_views < 0:
                        best[0] = 'p1'
                        predicted_for_next_30[:] = []
                        for i in range(len(old_views) + 1, len(old_views) + 8, 1):
                            predicted_for_next_30.append(p1[0] * i + p1[1])
                        increase_in_predicted_views = int(predicted_for_next_30[1]) - int(predicted_for_next_30[0])

                        # elif best[0] == "p3":
                        #    predicted_for_next_30.append(p3[0] * i ** 3 + p3[1] * i ** 2 + p3[2] * i + p3[3])

            # print(increase_in_predicted_views)
            # #print(len(predicted_dates),len(predicted_for_next_30))
            # for i,j in zip(views,predicted_old_views):
            #    #print(i,j)
            # print(best)
            old_views[:] = []
            old_dates[:] = []
            increse_in_old_views[:] = []
            increse_in_old_views = [0]

            count_1 = 0
            for k in c1:
                if count_1 == 0:
                    old_views.append(k.view)
                    old_dates.append(k.date1)
                else:
                    increse_in_old_views.append(k.view - old_views[count_1 - 1])
                    old_views.append(k.view)
                    old_dates.append(k.date1)
                count_1 = count_1 + 1
            predicted_old_views[:] = []
            if best[0] == 'p1':
                for i in range(len(old_views)):
                    predicted_old_views.append(p1[0] * i + p1[1])
            elif best[0] == 'p2':
                for i in range(len(old_views)):
                    predicted_old_views.append(p2[0] * i ** 2 + p2[1] * i + p2[2])
            elif best[0] == 'p3':
                for i in range(len(old_views)):
                    predicted_old_views.append(p3[0] * i ** 3 + p3[1] * i ** 2 + p3[2] * i + p3[3])
            old_views1 = old_views
            increse_in_old_views1 = increse_in_old_views
            predicted_old_views1 = predicted_old_views
            old_dates1 = old_dates
            accuracy_in_old_views1 = accuracy_in_old_views
            # print(accuracy_in_old_views1)
            old_views1 = old_views1[::-1]
            increse_in_old_views1 = increse_in_old_views1[::-1]
            predicted_old_views1 = predicted_old_views1[::-1]
            old_dates1 = old_dates1[::-1]
            accuracy_in_old_views1 = accuracy_in_old_views1[::-1]
            if best[0] == 'p1':
                avg_accuracy = accuracies['p1']
                avg_accuracy = '%.5f' % (avg_accuracy)
            elif best[0] == 'p2':
                avg_accuracy = accuracies['p2']
                avg_accuracy = '%.5f' % (avg_accuracy)
            else:
                avg_accuracy = accuracies['p3']
                avg_accuracy = '%.5f' % (avg_accuracy)

            user1 = users.objects.get(pk=request.session['User_Id'])
            User_Detail = user1
            return render(request, 'users/user_views_analysis.html',
                          {'User_Detail': User_Detail, 'Channel_Main_Data': channel_main_data,
                           'old_views': old_views,
                           'predicted_old_views': predicted_old_views, 'old_dates': old_dates,
                           'count_1': count_1,
                           'predicted_for_next_30': predicted_for_next_30,
                           'predicted_dates': predicted_dates,
                           'increse_in_old_views': increse_in_old_views,
                           'increase_in_predicted_views': increase_in_predicted_views,
                           'table_old_views': zip(old_dates1, old_views1, increse_in_old_views1,
                                                  predicted_old_views1,
                                                  accuracy_in_old_views1),
                           'avg_accuracy': avg_accuracy,
                           'Channel_Sub_Data': channel_sub_data,
                           'type': 'Total',
                           'label1': 'Increments in Views',
                           'label2': 'Prediction of Daily Views Increase For Next 7 Days',
                           'label3': 'Accuracy On Previous Data Available',
                           'label4': 'Total Views for of Previous Data Available',
                           'label5': 'Predicted Views for Next 30 Days',
                           'label6': 'History of Previous Predictions'})
            '''
        else:
            c1 = channel_sub_data1
            # print(len(channel_sub_data1))
            old_dates = []
            old_views = []
            increse_in_old_views = [0]
            count_1 = 0
            for k in channel_sub_data1:
                if count_1 == 0:
                    old_views.append(k.view)
                    old_dates.append(k.date1)
                else:
                    increse_in_old_views.append(k.view - old_views[count_1 - 1])
                    old_views.append(k.view)
                    old_dates.append(k.date1)
                count_1 = count_1 + 1
                ##print(increse_in_old_views)

                # prediction for all available old views
            V1 = old_views[:len(old_views) - 1]
            X1 = []
            for i in range(len(V1)):
                X1.append(i)
            actual = old_views[-1]
            p1 = polyfit(X1, V1, 1)
            p2 = polyfit(X1, V1, 2)
            p3 = polyfit(X1, V1, 3)
            p4 = polyfit(X1, V1, 4)
            p5 = polyfit(X1, V1, 5)
            predicted_p1 = p1[0] * len(uvsub) + p1[1]
            predicted_p2 = p2[0] * len(uvsub) ** 2 + p2[1] * len(uvsub) + p2[2]
            predicted_p3 = p3[0] * len(uvsub) ** 3 + p3[1] * len(uvsub) ** 2 + p3[2] * len(uvsub) + p3[3]
            predicted_p4 = p4[0] * len(uvsub) ** 4 + p4[1] * len(uvsub) ** 3 + p4[2] * len(uvsub) ** 2 + p4[
                                                                                                             3] * len(
                uvsub) + p4[4]
            predicted_p5 = p5[0] * len(uvsub) ** 5 + p5[1] * len(uvsub) ** 4 + p5[2] * len(uvsub) ** 3 + p5[
                                                                                                             3] * len(
                uvsub) ** 2 + p5[4] * len(uvsub) + p5[5]
            accuracy_p1 = 100 - abs((predicted_p1 - actual) / actual) * 100
            accuracy_p2 = 100 - abs((predicted_p2 - actual) / actual) * 100
            accuracy_p3 = 100 - abs((predicted_p3 - actual) / actual) * 100
            accuracy_p4 = 100 - abs((predicted_p4 - actual) / actual) * 100
            accuracy_p5 = 100 - abs((predicted_p5 - actual) / actual) * 100
            accuracies = {'p1': accuracy_p1, 'p2': accuracy_p2, 'p3': accuracy_p3, 'p4': accuracy_p4,
                          'p5': accuracy_p5}
            ##print(accuracy_p1,accuracy_p2,accuracy_p3,accuracy_p4,accuracy_p5)
            best = []
            predicted_old_views = []
            if accuracy_p1 > accuracy_p2 and accuracy_p1 > accuracy_p3 and accuracy_p1 > accuracy_p4 and accuracy_p1 > accuracy_p5:
                for i in range(len(old_views)):
                    predicted_old_views.append(p1[0] * i + p1[1])
                best.append("p1")
            elif accuracy_p2 > accuracy_p1 and accuracy_p2 > accuracy_p3 and accuracy_p2 > accuracy_p4 and accuracy_p2 > accuracy_p5:
                for i in range(len(old_views)):
                    predicted_old_views.append(p2[0] * i ** 2 + p2[1] * i + p2[2])
                best.append("p2")
            elif accuracy_p3 > accuracy_p1 and accuracy_p3 > accuracy_p2 and accuracy_p3 > accuracy_p4 and accuracy_p3 > accuracy_p5:
                for i in range(len(old_views)):
                    predicted_old_views.append(p3[0] * i ** 3 + p3[1] * i ** 2 + p3[2] * i + p3[3])
                best.append("p3")
            elif accuracy_p4 > accuracy_p1 and accuracy_p4 > accuracy_p2 and accuracy_p4 > accuracy_p3 and accuracy_p4 > accuracy_p5:
                for i in range(len(old_views)):
                    predicted_old_views.append(p4[0] * i ** 4 + p4[1] * i ** 3 + p4[2] * i ** 2 + p4[3] * i + p4[4])
                best.append("p4")
            else:
                for i in range(len(old_views)):
                    predicted_old_views.append(
                        p5[0] * i ** 5 + p5[1] * i ** 4 + p5[2] * i ** 3 + p5[3] * i ** 2 + p5[4] * i + p5[5])
                best.append("p5")

                # old views,old_views_increment,prediction_old,accuracy
            accuracy_in_old_views = []
            for i in range(len(old_views)):
                accuracy_in_old_views.append(
                    100 - abs((predicted_old_views[i] - old_views[i]) / old_views[i]))

                # prediction for next 30 days
            predicted_for_next_30 = []
            for i in range(len(old_views) + 1, len(old_views) + 31, 1):
                if best[0] == "p1":
                    predicted_for_next_30.append(p1[0] * i + p1[1])
                elif best[0] == "p2":
                    predicted_for_next_30.append(p2[0] * i ** 2 + p2[1] * i + p2[2])
                elif best[0] == "p3":
                    predicted_for_next_30.append(p3[0] * i ** 3 + p3[1] * i ** 2 + p3[2] * i + p3[3])
                elif best[0] == "p4":
                    predicted_for_next_30.append(
                        p4[0] * i ** 4 + p4[1] * i ** 3 + p4[2] * i ** 2 + p4[3] * i + p4[4])
                else:
                    predicted_for_next_30.append(
                        p5[0] * i ** 5 + p5[1] * i ** 4 + p5[2] * i ** 3 + p5[3] * i ** 2 + p5[4] * i + p5[5])
            # print('\n',p2,'\n\n')
            # print(predicted_for_next_30)
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

            increase_in_predicted_views = int(predicted_for_next_30[1]) - int(predicted_for_next_30[0])

            # print(increase_in_predicted_views)
            # #print(len(predicted_dates),len(predicted_for_next_30))
            # for i,j in zip(views,predicted_old_views):
            #    #print(i,j)
            # print(best)
            old_views1 = old_views
            increse_in_old_views1 = increse_in_old_views
            predicted_old_views1 = predicted_old_views
            old_dates1 = old_dates
            accuracy_in_old_views1 = accuracy_in_old_views
            # print(accuracy_in_old_views1)
            old_views1 = old_views1[::-1]
            increse_in_old_views1 = increse_in_old_views1[::-1]
            predicted_old_views1 = predicted_old_views1[::-1]
            old_dates1 = old_dates1[::-1]
            accuracy_in_old_views1 = accuracy_in_old_views1[::-1]
            if best[0] == 'p1':
                avg_accuracy = accuracies['p1']
                avg_accuracy = '%.5f' % (avg_accuracy)
            elif best[0] == 'p2':
                avg_accuracy = accuracies['p2']
                avg_accuracy = '%.5f' % (avg_accuracy)
            elif best[0] == 'p3':
                avg_accuracy = accuracies['p3']
                avg_accuracy = '%.5f' % (avg_accuracy)
            elif best[0] == 'p4':
                avg_accuracy = accuracies['p4']
                avg_accuracy = '%.5f' % (avg_accuracy)
            else:
                avg_accuracy = accuracies['p5']
                avg_accuracy = '%.5f' % (avg_accuracy)
            user1 = users.objects.get(pk=request.session['User_Id'])
            User_Detail = user1
            return render(request, 'users/user_views_analysis.html',
                          {'User_Detail': User_Detail, 'Channel_Main_Data': channel_main_data,
                           'old_views': old_views,
                           'predicted_old_views': predicted_old_views, 'old_dates': old_dates,
                           'count_1': count_1,
                           'predicted_for_next_30': predicted_for_next_30,
                           'predicted_dates': predicted_dates,
                           'increse_in_old_views': increse_in_old_views,
                           'increase_in_predicted_views': increase_in_predicted_views,
                           'table_old_views': zip(old_dates1, old_views1, increse_in_old_views1,
                                                  predicted_old_views1,
                                                  accuracy_in_old_views1),
                           'avg_accuracy': avg_accuracy,
                           'Channel_Sub_Data': channel_sub_data,
                           'type': 'Total',
                           'label1': 'Increments in Views',
                           'label2': 'Prediction of Daily Views Increase For Next 7 Days',
                           'label3': 'Accuracy On Previous Data Available',
                           'label4': 'Total Views for of Previous Data Available',
                           'label5': 'Predicted Views for Next 15 Days',
                           'label6': 'History of Previous Predictions'})
        '''
        else:
            dates = []
            views = []
            likes = []
            dislikes = []
            for i in uvsub:
                dates.append(i.date1)
                views.append(i.view)
                likes.append(i.likes)
                dislikes.append(i.dislikes)
            return render(request, 'users/less_than_7_days.html', {'User_Detail': User_Detail,
                                                               'status': 'We are currently analysing your Video....We will notify you on your email after ' + str(
                                                                   8 - len(uvsub)) + ' days',
                                                               'uvmain': uvmain, 'uvsub': uvsub,
                                                               'user_view_table': zip(dates, views, likes,
                                                                                      dislikes)})

    else:
        return HttpResponseRedirect('/Home/')

def bimoonthly_view_video_analysis(request, video_id):
    if 'User_Id' in request.session:
        user1 = users.objects.get(pk=request.session['User_Id'])
        User_Detail = user1
        uvmain = video_main.objects.get(user_id=user1.pk, id=video_id)
        uvsub = video_sub.objects.filter(video_main_id=video_main.objects.get(id=uvmain.id)).order_by('-date1')
        if len(uvsub) > 7:
            # print('inside123')
            channel_main_data = video_main.objects.get(user_id=user1.pk, id=uvmain.id)
            channel_sub_data = video_sub.objects.filter(
                video_main_id=video_main.objects.get(id=uvmain.id)).order_by('-date1')
            channel_sub_data1 = video_sub.objects.filter(
                video_main_id=video_main.objects.get(id=uvmain.id)).order_by('date1')
            channel_sub_data1 = channel_sub_data1[len(channel_sub_data1) - 15:]
            # print(len(channel_sub_data1))
            old_dates = []
            old_views = []
            increse_in_old_views = [0]
            count_1 = 0
            for k in channel_sub_data1:
                if count_1 == 0:
                    old_views.append(k.view)
                    old_dates.append(k.date1)
                else:
                    increse_in_old_views.append(k.view - old_views[count_1 - 1])
                    old_views.append(k.view)
                    old_dates.append(k.date1)
                count_1 = count_1 + 1
                # print(increse_in_old_views)

                # prediction for all available old views
            V1 = old_views[:len(old_views) - 1]
            X1 = []
            for i in range(len(V1)):
                X1.append(i)
            # print(V1)
            actual = old_views[-1]
            p1 = polyfit(X1, V1, 1)
            p2 = polyfit(X1, V1, 2)
            p3 = polyfit(X1, V1, 3)
            p4 = polyfit(X1, V1, 4)
            p5 = polyfit(X1, V1, 5)

            predicted_p1 = p1[0] * len(uvsub) + p1[1]
            predicted_p2 = p2[0] * len(uvsub) ** 2 + p2[1] * len(uvsub) + p2[2]
            predicted_p3 = p3[0] * len(uvsub) ** 3 + p3[1] * len(uvsub) ** 2 + p3[2] * len(uvsub) + p3[3]
            predicted_p4 = p4[0] * len(uvsub) ** 4 + p4[1] * len(uvsub) ** 3 + p4[2] * len(uvsub) ** 2 + p4[
                                                                                                             3] * len(
                uvsub) + p4[4]
            predicted_p5 = p5[0] * len(uvsub) ** 5 + p5[1] * len(uvsub) ** 4 + p5[2] * len(uvsub) ** 3 + p5[
                                                                                                             3] * len(
                uvsub) ** 2 + p5[4] * len(uvsub) + p5[5]

            accuracy_p1 = 100 - abs((predicted_p1 - actual) / actual) * 100
            accuracy_p2 = 100 - abs((predicted_p2 - actual) / actual) * 100
            accuracy_p3 = 100 - abs((predicted_p3 - actual) / actual) * 100
            accuracy_p4 = 100 - abs((predicted_p4 - actual) / actual) * 100
            accuracy_p5 = 100 - abs((predicted_p5 - actual) / actual) * 100

            best = []
            predicted_old_views = []
            if accuracy_p2 > 99.8:
                for i in range(len(old_views)):
                    predicted_old_views.append(p1[0] * i + p1[1])
                best.append("p2")
            elif accuracy_p1 > accuracy_p2 and accuracy_p1 > accuracy_p3 and accuracy_p1 > accuracy_p4 and accuracy_p1 > accuracy_p5:
                for i in range(len(old_views)):
                    predicted_old_views.append(p1[0] * i + p1[1])
                best.append("p1")
            elif accuracy_p2 > accuracy_p1 and accuracy_p2 > accuracy_p3 and accuracy_p2 > accuracy_p4 and accuracy_p2 > accuracy_p5:
                for i in range(len(old_views)):
                    predicted_old_views.append(p2[0] * i ** 2 + p2[1] * i + p2[2])
                best.append("p2")
            elif accuracy_p3 > accuracy_p1 and accuracy_p3 > accuracy_p2 and accuracy_p3 > accuracy_p4 and accuracy_p3 > accuracy_p5:
                for i in range(len(old_views)):
                    predicted_old_views.append(p3[0] * i ** 3 + p3[1] * i ** 2 + p3[2] * i + p3[3])
                best.append("p3")
            elif accuracy_p4 > accuracy_p1 and accuracy_p4 > accuracy_p2 and accuracy_p4 > accuracy_p3 and accuracy_p4 > accuracy_p5:
                for i in range(len(old_views)):
                    predicted_old_views.append(p4[0] * i ** 4 + p4[1] * i ** 3 + p4[2] * i ** 2 + p4[3] * i + p4[4])
                best.append("p4")
            else:
                for i in range(len(old_views)):
                    predicted_old_views.append(
                        p5[0] * i ** 5 + p5[1] * i ** 4 + p5[2] * i ** 3 + p5[3] * i ** 2 + p5[4] * i + p5[5])
                best.append("p5")

                # old views,old_views_increment,prediction_old,accuracy
            accuracy_in_old_views = []
            for i in range(len(old_views)):
                accuracy_in_old_views.append(
                    100 - abs((predicted_old_views[i] - old_views[i]) / old_views[i]))

                # prediction for next 30 days
            predicted_for_next_30 = []
            for i in range(len(old_views) + 1, len(old_views) + 16, 1):
                if best[0] == "p1":
                    predicted_for_next_30.append(p1[0] * i + p1[1])
                elif best[0] == "p2":
                    predicted_for_next_30.append(p2[0] * i ** 2 + p2[1] * i + p2[2])
                elif best[0] == "p3":
                    predicted_for_next_30.append(p3[0] * i ** 3 + p3[1] * i ** 2 + p3[2] * i + p3[3])
                elif best[0] == "p4":
                    predicted_for_next_30.append(
                        p4[0] * i ** 4 + p4[1] * i ** 3 + p4[2] * i ** 2 + p4[3] * i + p4[4])
                else:
                    predicted_for_next_30.append(
                        p5[0] * i ** 5 + p5[1] * i ** 4 + p5[2] * i ** 3 + p5[3] * i ** 2 + p5[4] * i + p5[5])
            # print(best[0])
            # print(predicted_for_next_30)
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
            # print(increase_in_predicted_views)
            # #print(len(predicted_dates),len(predicted_for_next_30))
            # for i,j in zip(views,predicted_old_views):
            #    #print(i,j)

            old_views1 = old_views
            increse_in_old_views1 = increse_in_old_views
            predicted_old_views1 = predicted_old_views
            old_dates1 = old_dates
            accuracy_in_old_views1 = accuracy_in_old_views
            # print(accuracy_in_old_views1)
            old_views1 = old_views1[::-1]
            increse_in_old_views1 = increse_in_old_views1[::-1]
            predicted_old_views1 = predicted_old_views1[::-1]
            old_dates1 = old_dates1[::-1]
            accuracy_in_old_views1 = accuracy_in_old_views1[::-1]
            avg_accuracy = average(accuracy_in_old_views)
            avg_accuracy = '%.5f' % (avg_accuracy)

            user1 = users.objects.get(pk=request.session['User_Id'])
            User_Detail = user1
            return render(request, 'users/user_views_analysis.html',
                          {'User_Detail': User_Detail, 'Channel_Main_Data': channel_main_data,
                           'old_views': old_views,
                           'predicted_old_views': predicted_old_views, 'old_dates': old_dates,
                           'count_1': count_1,
                           'predicted_for_next_30': predicted_for_next_30,
                           'predicted_dates': predicted_dates,
                           'increse_in_old_views': increse_in_old_views,
                           'increase_in_predicted_views': increase_in_predicted_views,
                           'table_old_views': zip(old_dates1, old_views1, increse_in_old_views1,
                                                  predicted_old_views1,
                                                  accuracy_in_old_views1),
                           'avg_accuracy': avg_accuracy,
                           'Channel_Sub_Data': channel_sub_data,
                           'type': 'Total',
                           'label1': 'Increments in Views',
                           'label2': 'Prediction of Daily Views Increase For Next 7 Days',
                           'label3': 'Accuracy On Previous Data Available',
                           'label4': 'Total Views for of Previous Data Available',
                           'label5': 'Predicted Views for Next 7 Days',
                           'label6': 'History of Previous Predictions'})
        else:
            dates = []
            views = []
            likes = []
            dislikes = []
            for i in uvsub:
                dates.append(i.date1)
                views.append(i.view)
                likes.append(i.likes)
                dislikes.append(i.dislikes)
            return render(request, 'users/less_than_7_days.html', {'User_Detail': User_Detail,
                                                                   'status': 'We are currently analysing your Video....We will notify you on your email after ' + str(
                                                                       8 - len(uvsub)) + ' days',
                                                                   'uvmain': uvmain, 'uvsub': uvsub,
                                                                   'user_view_table': zip(dates, views, likes,
                                                                                          dislikes)})
    else:
        return HttpResponseRedirect('/Home/')

def monthly_view_video_analysis(request, video_id):
    if 'User_Id' in request.session:
        user1 = users.objects.get(pk=request.session['User_Id'])
        User_Detail = user1
        uvmain = video_main.objects.get(user_id=user1.pk, id=video_id)
        uvsub = video_sub.objects.filter(video_main_id=video_main.objects.get(id=uvmain.id)).order_by('-date1')
        channel_main_data = video_main.objects.get(user_id=user1.pk, id=uvmain.id)
        channel_sub_data = video_sub.objects.filter(
            video_main_id=video_main.objects.get(id=uvmain.id)).order_by('-date1')
        channel_sub_data1 = video_sub.objects.filter(
            video_main_id=video_main.objects.get(id=uvmain.id)).order_by('date1')
        c1 = channel_sub_data1
        channel_sub_data1 = channel_sub_data1[len(channel_sub_data1) - 30:]
        channel_sub_data1 = channel_sub_data1[10:]
        # print(len(channel_sub_data1))
        old_dates = []
        old_views = []
        increse_in_old_views = [0]
        count_1 = 0
        for k in channel_sub_data1:
            if count_1 == 0:
                old_views.append(k.view)
                old_dates.append(k.date1)
            else:
                increse_in_old_views.append(k.view - old_views[count_1 - 1])
                old_views.append(k.view)
                old_dates.append(k.date1)
            count_1 = count_1 + 1
            ##print(increse_in_old_views)

            # prediction for all available old views
        V1 = old_views[:len(old_views) - 1]
        X1 = []
        for i in range(len(V1)):
            X1.append(i)
        actual = old_views[-1]
        p1 = polyfit(X1, V1, 1)
        p2 = polyfit(X1, V1, 2)
        p3 = polyfit(X1, V1, 3)

        predicted_p1 = p1[0] * len(uvsub) + p1[1]
        predicted_p2 = p2[0] * len(uvsub) ** 2 + p2[1] * len(uvsub) + p2[2]
        predicted_p3 = p3[0] * len(uvsub) ** 3 + p3[1] * len(uvsub) ** 2 + p3[2] * len(uvsub) + p3[3]

        accuracy_p1 = 100 - abs((predicted_p1 - actual) / actual) * 100
        accuracy_p2 = 100 - abs((predicted_p2 - actual) / actual) * 100
        accuracy_p3 = 100 - abs((predicted_p3 - actual) / actual) * 100
        accuracies = {'p1': accuracy_p1, 'p2': accuracy_p2, 'p3': accuracy_p3}
        ##print(accuracy_p1,accuracy_p2,accuracy_p3,accuracy_p4,accuracy_p5)
        best = []
        predicted_old_views = []
        if accuracy_p1 > accuracy_p2 and accuracy_p1 > accuracy_p3:
            for i in range(len(old_views)):
                predicted_old_views.append(p1[0] * i + p1[1])
            best.append("p1")
        elif accuracy_p2 > accuracy_p1 and accuracy_p2 > accuracy_p3:
            for i in range(len(old_views)):
                predicted_old_views.append(p2[0] * i ** 2 + p2[1] * i + p2[2])
            best.append("p2")
        elif accuracy_p3 > accuracy_p1 and accuracy_p3 > accuracy_p2:
            for i in range(len(old_views)):
                predicted_old_views.append(p3[0] * i ** 3 + p3[1] * i ** 2 + p3[2] * i + p3[3])
            best.append("p3")

        # old views,old_views_increment,prediction_old,accuracy
        accuracy_in_old_views = []
        for i in range(len(old_views)):
            accuracy_in_old_views.append(
                100 - abs((predicted_old_views[i] - old_views[i]) / old_views[i]))

            # prediction for next 30 days
        predicted_for_next_30 = []

        for i in range(len(old_views) + 11, len(old_views) + 42, 1):
            if best[0] == "p1":
                predicted_for_next_30.append(p1[0] * i + p1[1])
            elif best[0] == "p2":
                predicted_for_next_30.append(p2[0] * i ** 2 + p2[1] * i + p2[2])
            elif best[0] == "p3":
                predicted_for_next_30.append(p3[0] * i ** 3 + p3[1] * i ** 2 + p3[2] * i + p3[3])

        # print('\n',p2,'\n\n')
        # print(predicted_for_next_30)
        predicted_dates = []
        for i in range(31):
            if i == 0:
                d = datetime.strptime(old_dates[-1], "%Y-%m-%d")
                y = d + timedelta(days=1)
                predicted_dates.append(y.strftime("%Y-%m-%d"))
            else:
                d = datetime.strptime(predicted_dates[-1], "%Y-%m-%d")
                y = d + timedelta(days=1)
                predicted_dates.append(y.strftime("%Y-%m-%d"))

        increase_in_predicted_views = int(predicted_for_next_30[1]) - int(predicted_for_next_30[0])
        if increase_in_predicted_views < 0:
            predicted_for_next_30[:] = []
            if best[0] == 'p1':
                best[0] = 'p2'
                for i in range(len(old_views) + 11, len(old_views) + 42, 1):
                    predicted_for_next_30.append(p2[0] * i ** 2 + p2[1] * i + p2[2])
                increase_in_predicted_views = int(predicted_for_next_30[1]) - int(predicted_for_next_30[0])
                if increase_in_predicted_views < 0:
                    best[0] = 'p3'
                    predicted_for_next_30[:] = []
                    for i in range(len(old_views) + 11, len(old_views) + 42, 1):
                        predicted_for_next_30.append(p3[0] * i ** 3 + p3[1] * i ** 2 + p3[2] * i + p3[3])
                    increase_in_predicted_views = int(predicted_for_next_30[1]) - int(predicted_for_next_30[0])
            elif best[0] == 'p2':
                best[0] = 'p1'
                for i in range(len(old_views) + 11, len(old_views) + 42, 1):
                    predicted_for_next_30.append(p1[0] * i + p1[1])
                increase_in_predicted_views = int(predicted_for_next_30[1]) - int(predicted_for_next_30[0])
                if increase_in_predicted_views < 0:
                    best[0] = 'p3'
                    predicted_for_next_30[:] = []
                    for i in range(len(old_views) + 11, len(old_views) + 42, 1):
                        predicted_for_next_30.append(p3[0] * i ** 3 + p3[1] * i ** 2 + p3[2] * i + p3[3])
                    increase_in_predicted_views = int(predicted_for_next_30[1]) - int(predicted_for_next_30[0])

            elif best[0] == 'p3':
                best[0] = 'p2'
                for i in range(len(old_views) + 11, len(old_views) + 42, 1):
                    predicted_for_next_30.append(p2[0] * i ** 2 + p2[1] * i + p2[2])
                increase_in_predicted_views = int(predicted_for_next_30[1]) - int(predicted_for_next_30[0])
                if increase_in_predicted_views < 0:
                    best[0] = 'p1'
                    predicted_for_next_30[:] = []
                    for i in range(len(old_views) + 11, len(old_views) + 42, 1):
                        predicted_for_next_30.append(p1[0] * i + p1[1])
                    increase_in_predicted_views = int(predicted_for_next_30[1]) - int(predicted_for_next_30[0])

                    # elif best[0] == "p3":
                    #    predicted_for_next_30.append(p3[0] * i ** 3 + p3[1] * i ** 2 + p3[2] * i + p3[3])

        # print(increase_in_predicted_views)
        # #print(len(predicted_dates),len(predicted_for_next_30))
        # for i,j in zip(views,predicted_old_views):
        #    #print(i,j)
        # print(best)
        old_views[:] = []
        old_dates[:] = []
        increse_in_old_views[:] = []
        increse_in_old_views = [0]

        count_1 = 0
        for k in c1:
            if count_1 == 0:
                old_views.append(k.view)
                old_dates.append(k.date1)
            else:
                increse_in_old_views.append(k.view - old_views[count_1 - 1])
                old_views.append(k.view)
                old_dates.append(k.date1)
            count_1 = count_1 + 1
        predicted_old_views[:] = []
        if best[0] == 'p1':
            for i in range(len(old_views)):
                predicted_old_views.append(p1[0] * i + p1[1])
        elif best[0] == 'p2':
            for i in range(len(old_views)):
                predicted_old_views.append(p2[0] * i ** 2 + p2[1] * i + p2[2])
        elif best[0] == 'p3':
            for i in range(len(old_views)):
                predicted_old_views.append(p3[0] * i ** 3 + p3[1] * i ** 2 + p3[2] * i + p3[3])
        old_views1 = old_views
        increse_in_old_views1 = increse_in_old_views
        predicted_old_views1 = predicted_old_views
        old_dates1 = old_dates
        accuracy_in_old_views1 = accuracy_in_old_views
        # print(accuracy_in_old_views1)
        old_views1 = old_views1[::-1]
        increse_in_old_views1 = increse_in_old_views1[::-1]
        predicted_old_views1 = predicted_old_views1[::-1]
        old_dates1 = old_dates1[::-1]
        accuracy_in_old_views1 = accuracy_in_old_views1[::-1]
        if best[0] == 'p1':
            avg_accuracy = accuracies['p1']
            avg_accuracy = '%.5f' % (avg_accuracy)
        elif best[0] == 'p2':
            avg_accuracy = accuracies['p2']
            avg_accuracy = '%.5f' % (avg_accuracy)
        else:
            avg_accuracy = accuracies['p3']
            avg_accuracy = '%.5f' % (avg_accuracy)

        user1 = users.objects.get(pk=request.session['User_Id'])
        User_Detail = user1
        return render(request, 'users/user_views_analysis.html',
                      {'User_Detail': User_Detail, 'Channel_Main_Data': channel_main_data,
                       'old_views': old_views,
                       'predicted_old_views': predicted_old_views, 'old_dates': old_dates,
                       'count_1': count_1,
                       'predicted_for_next_30': predicted_for_next_30,
                       'predicted_dates': predicted_dates,
                       'increse_in_old_views': increse_in_old_views,
                       'increase_in_predicted_views': increase_in_predicted_views,
                       'table_old_views': zip(old_dates1, old_views1, increse_in_old_views1,
                                              predicted_old_views1,
                                              accuracy_in_old_views1),
                       'avg_accuracy': avg_accuracy,
                       'Channel_Sub_Data': channel_sub_data,
                       'type': 'Total',
                       'label1': 'Increments in Views',
                       'label2': 'Prediction of Daily Views Increase For Next 7 Days',
                       'label3': 'Accuracy On Previous Data Available',
                       'label4': 'Total Views for of Previous Data Available',
                       'label5': 'Predicted Views for Next 30 Days',
                       'label6': 'History of Previous Predictions'})

    else:
        return HttpResponseRedirect('/Home/')





def view_channel_dashboard(request, channel_id):
    if 'User_Id' in request.session:
        channel_main_data = user_channel_main.objects.get(pk=channel_id)
        channel_sub_data = user_channel_sub.objects.filter(
            channel_id=user_channel_main.objects.get(pk=channel_id)).order_by('-date1')
        channel_sub_data1 = user_channel_sub.objects.filter(
            channel_id=user_channel_main.objects.get(pk=channel_id)).order_by('date1')
        if len(channel_sub_data) > 7:

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
            # print(increse_in_old_views)

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
                avg_accuracy= float(100 - abs((predicted_p2 - actual) / actual) * 100)
                best.append("p2")
            else:
                for i in range(len(old_views)):
                    predicted_old_views.append(p1[0] * i + p1[1])
                avg_accuracy = float(100 - abs((predicted_p1 - actual) / actual) * 100)
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

            # #print(len(predicted_dates),len(predicted_for_next_30))
            # for i,j in zip(views,predicted_old_views):
            #    #print(i,j)

            old_views1 = old_views
            increse_in_old_views1 = increse_in_old_views
            predicted_old_views1 = predicted_old_views
            old_dates1 = old_dates
            accuracy_in_old_views1 = accuracy_in_old_views
            # print(accuracy_in_old_views1)
            old_views1 = old_views1[::-1]
            increse_in_old_views1 = increse_in_old_views1[::-1]
            predicted_old_views1 = predicted_old_views1[::-1]
            old_dates1 = old_dates1[::-1]
            accuracy_in_old_views1 = accuracy_in_old_views1[::-1]
            #avg_accuracy = average(accuracy_in_old_views)
            avg_accuracy = '%.5f' % (avg_accuracy)

            if 'User_Id' in request.session:
                user1 = users.objects.get(pk=request.session['User_Id'])
                User_Detail = user1
                return render(request, 'users/user_channel_analysis.html',
                              {'User_Detail': User_Detail, 'Channel_Main_Data': channel_main_data,
                               'old_views': old_views,
                               'predicted_old_views': predicted_old_views, 'old_dates': old_dates, 'count_1': count_1,
                               'predicted_for_next_30': predicted_for_next_30, 'predicted_dates': predicted_dates,
                               'increse_in_old_views': increse_in_old_views,
                               'increase_in_predicted_views': increase_in_predicted_views,
                               'table_old_views': zip(old_dates1, old_views1, increse_in_old_views1,
                                                      predicted_old_views1,
                                                      accuracy_in_old_views1),
                               'avg_accuracy': avg_accuracy,
                               'Channel_Sub_Data': channel_sub_data,
                               'type': 'Total',
                               'type1': 'View',
                               'label1': 'Increments in Views',
                               'label2': 'Prediction of Daily Views Increase For Next 30 Days',
                               'label3': 'Accuracy On Previous Data Available',
                               'label4': 'Total Views for of Previous Data Available',
                               'label5': 'Predicted Views for Next 30 Days',
                               'label6': 'History of Previous Predictions'})
            else:
                return render(request, 'users/user_channel_analysis.html',
                              {'User_Detail': '', 'Channel_Main_Data': channel_main_data, 'old_views': old_views,
                               'predicted_old_views': predicted_old_views, 'old_dates': old_dates,
                               'count_1': int(count_1),
                               'predicted_for_next_30': predicted_for_next_30, 'predicted_dates': predicted_dates,
                               'increse_in_old_views': increse_in_old_views,
                               'increase_in_predicted_views': increase_in_predicted_views,
                               'table_old_views': zip(old_dates1, old_views1, increse_in_old_views1,
                                                      predicted_old_views1,
                                                      accuracy_in_old_views1),
                               'avg_accuracy': avg_accuracy,
                               'Channel_Sub_Data': channel_sub_data,
                               'type': 'Total',
                               'type1': 'View',
                               'label1': 'Increments in Views',
                               'label2': 'Prediction of Daily Views Increase For Next 30 Days',
                               'label3': 'Accuracy On Previous Data Available',
                               'label4': 'Total Views for of Previous Data Available',
                               'label5': 'Predicted Views for Next 30 Days',
                               'label6': 'History of Previous Predictions'})
        else:
            dates = []
            views = []
            subscribers = []
            user1 = users.objects.get(pk=request.session['User_Id'])
            User_Detail = user1
            for i in channel_sub_data1:
                dates.append(i.date1)
                views.append(i.view_count)
                subscribers.append(i.subscriber_count)
            return render(request, 'users/less_than_7_days_channel.html', {'User_Detail': User_Detail,
                                                                           'status': 'We are currently analysing your Video....We will notify you on your email after ' + str(
                                                                               8 - len(channel_sub_data1)) + ' days',
                                                                           'ucmain': channel_main_data,
                                                                           'ucsub': channel_sub_data1,
                                                                           'user_view_table': zip(dates, views,
                                                                                                  subscribers, )})
    else:
        return HttpResponseRedirect("/Home/")

def weekly_view_channel_analysis(request, channel_id):
    if 'User_Id' in request.session:
        channel_main_data = user_channel_main.objects.get(pk=channel_id)
        channel_sub_data = user_channel_sub.objects.filter(
            channel_id=user_channel_main.objects.get(pk=channel_id)).order_by('-date1')
        channel_sub_data1 = user_channel_sub.objects.filter(
            channel_id=user_channel_main.objects.get(pk=channel_id)).order_by('date1')
        channel_sub_data1 = channel_sub_data1[len(channel_sub_data1) - 7:]
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
            # print(increse_in_old_views)

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
            avg_accuracy = float(100 - abs((predicted_p2 - actual) / actual) * 100)
            best.append("p2")
        else:
            for i in range(len(old_views)):
                predicted_old_views.append(p1[0] * i + p1[1])
            avg_accuracy = float(100 - abs((predicted_p1 - actual) / actual) * 100)
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

        # #print(len(predicted_dates),len(predicted_for_next_30))
        # for i,j in zip(views,predicted_old_views):
        #    #print(i,j)

        old_views1 = old_views
        increse_in_old_views1 = increse_in_old_views
        predicted_old_views1 = predicted_old_views
        old_dates1 = old_dates
        accuracy_in_old_views1 = accuracy_in_old_views
        # print(accuracy_in_old_views1)
        old_views1 = old_views1[::-1]
        increse_in_old_views1 = increse_in_old_views1[::-1]
        predicted_old_views1 = predicted_old_views1[::-1]
        old_dates1 = old_dates1[::-1]
        accuracy_in_old_views1 = accuracy_in_old_views1[::-1]
        #avg_accuracy = average(accuracy_in_old_views)
        avg_accuracy = '%.5f' % (avg_accuracy)

        user1 = users.objects.get(pk=request.session['User_Id'])
        User_Detail = user1
        return render(request, 'users/user_channel_analysis.html',
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
                       'type1': 'View',
                       'label1': 'Increments in Views', 'label2': 'Prediction of Daily Views Increase For Next Week',
                       'label3': 'Accuracy On Last Week Data Available',
                       'label4': 'Total Views for Week Data Available',
                       'label5': 'Predicted Views for Next Week', 'label6': 'History of Previous Predictions'})

    else:
        return HttpResponseRedirect("/Home/")

def bimonthly_view_channel_analysis(request, channel_id):
    if 'User_Id' in request.session:
        channel_main_data = user_channel_main.objects.get(pk=channel_id)
        channel_sub_data = user_channel_sub.objects.filter(
            channel_id=user_channel_main.objects.get(pk=channel_id)).order_by('-date1')
        channel_sub_data1 = user_channel_sub.objects.filter(
            channel_id=user_channel_main.objects.get(pk=channel_id)).order_by('date1')
        channel_sub_data1 = channel_sub_data1[len(channel_sub_data1) - 15:]
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
            # print(increse_in_old_views)

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
            avg_accuracy = float(100 - abs((predicted_p2 - actual) / actual) * 100)
            best.append("p2")
        else:
            for i in range(len(old_views)):
                predicted_old_views.append(p1[0] * i + p1[1])
            avg_accuracy = float(100 - abs((predicted_p1 - actual) / actual) * 100)
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

        # #print(len(predicted_dates),len(predicted_for_next_30))
        # for i,j in zip(views,predicted_old_views):
        #    #print(i,j)

        old_views1 = old_views
        increse_in_old_views1 = increse_in_old_views
        predicted_old_views1 = predicted_old_views
        old_dates1 = old_dates
        accuracy_in_old_views1 = accuracy_in_old_views
        # print(accuracy_in_old_views1)
        old_views1 = old_views1[::-1]
        increse_in_old_views1 = increse_in_old_views1[::-1]
        predicted_old_views1 = predicted_old_views1[::-1]
        old_dates1 = old_dates1[::-1]
        accuracy_in_old_views1 = accuracy_in_old_views1[::-1]
        #avg_accuracy = average(accuracy_in_old_views)
        avg_accuracy = '%.5f' % (avg_accuracy)

        user1 = users.objects.get(pk=request.session['User_Id'])
        User_Detail = user1
        return render(request, 'users/user_channel_analysis.html',
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
                       'type1': 'View',
                       'label1': 'Increments in Views', 'label2': 'Prediction of Daily Views Increase For Next 15 Days',
                       'label3': 'Accuracy On Last 15 Days Data Available',
                       'label4': 'Total Views for of Last 15 Days Data Available',
                       'label5': 'Predicted Views for Next 15 Days', 'label6': 'History of Previous Predictions'})

    else:
        return HttpResponseRedirect("/Home/")

def monthly_view_channel_analysis(request, channel_id):
    if 'User_Id' in request.session:
        channel_main_data = user_channel_main.objects.get(pk=channel_id)
        channel_sub_data = user_channel_sub.objects.filter(
            channel_id=user_channel_main.objects.get(pk=channel_id)).order_by('-date1')
        channel_sub_data1 = user_channel_sub.objects.filter(
            channel_id=user_channel_main.objects.get(pk=channel_id)).order_by('date1')
        channel_sub_data1 = channel_sub_data1[len(channel_sub_data1) - 30:]
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
            # print(increse_in_old_views)

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
            avg_accuracy = float(100 - abs((predicted_p2 - actual) / actual) * 100)
            best.append("p2")
        else:
            for i in range(len(old_views)):
                predicted_old_views.append(p1[0] * i + p1[1])
            avg_accuracy = float(100 - abs((predicted_p1 - actual) / actual) * 100)
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

        # #print(len(predicted_dates),len(predicted_for_next_30))
        # for i,j in zip(views,predicted_old_views):
        #    #print(i,j)

        old_views1 = old_views
        increse_in_old_views1 = increse_in_old_views
        predicted_old_views1 = predicted_old_views
        old_dates1 = old_dates
        accuracy_in_old_views1 = accuracy_in_old_views
        # print(accuracy_in_old_views1)
        old_views1 = old_views1[::-1]
        increse_in_old_views1 = increse_in_old_views1[::-1]
        predicted_old_views1 = predicted_old_views1[::-1]
        old_dates1 = old_dates1[::-1]
        accuracy_in_old_views1 = accuracy_in_old_views1[::-1]
        #avg_accuracy = average(accuracy_in_old_views)
        # print('%.5f' % (avg_accuracy))
        avg_accuracy = '%.5f' % (avg_accuracy)
        user1 = users.objects.get(pk=request.session['User_Id'])
        User_Detail = user1
        return render(request, 'users/user_channel_analysis.html',
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
                       'type1': 'View',
                       'label1': 'Increments in Views', 'label2': 'Prediction of Daily Views Increase For Next 30 Days',
                       'label3': 'Accuracy On Last Month Data Available',
                       'label4': 'Total Views for of Last month Data Available',
                       'label5': 'Predicted Views for Next 30 Days', 'label6': 'History of Previous Predictions'})

    else:
        return HttpResponseRedirect("/Home/")

def weekly_subs_channel_analysis(request, channel_id):
    if 'User_Id' in request.session:
        channel_main_data = user_channel_main.objects.get(pk=channel_id)
        channel_sub_data = user_channel_sub.objects.filter(
            channel_id=user_channel_main.objects.get(pk=channel_id)).order_by('-date1')
        channel_sub_data1 = user_channel_sub.objects.filter(
            channel_id=user_channel_main.objects.get(pk=channel_id)).order_by('date1')
        channel_sub_data1 = channel_sub_data1[len(channel_sub_data1) - 7:]
        old_dates = []
        old_views = []
        increse_in_old_views = [0]
        count_1 = 0
        for k in channel_sub_data1:
            if count_1 == 0:
                old_views.append(k.subscriber_count)
                old_dates.append(k.date1)
            else:
                increse_in_old_views.append(k.subscriber_count - old_views[count_1 - 1])
                old_views.append(k.subscriber_count)
                old_dates.append(k.date1)
            count_1 = count_1 + 1
            # print(increse_in_old_views)

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
            avg_accuracy = float(100 - abs((predicted_p2 - actual) / actual) * 100)
            best.append("p2")
        else:
            for i in range(len(old_views)):
                predicted_old_views.append(p1[0] * i + p1[1])
            avg_accuracy = float(100 - abs((predicted_p1 - actual) / actual) * 100)
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
        print(int(predicted_for_next_30[1]), int(predicted_for_next_30[0]), increase_in_predicted_views)
        # #print(len(predicted_dates),len(predicted_for_next_30))
        # for i,j in zip(views,predicted_old_views):
        #    #print(i,j)

        old_views1 = old_views
        increse_in_old_views1 = increse_in_old_views
        predicted_old_views1 = predicted_old_views
        old_dates1 = old_dates
        accuracy_in_old_views1 = accuracy_in_old_views
        # print(accuracy_in_old_views1)
        old_views1 = old_views1[::-1]
        increse_in_old_views1 = increse_in_old_views1[::-1]
        predicted_old_views1 = predicted_old_views1[::-1]
        old_dates1 = old_dates1[::-1]
        accuracy_in_old_views1 = accuracy_in_old_views1[::-1]
        #avg_accuracy = average(accuracy_in_old_views)
        # print('%.5f' % (avg_accuracy))
        avg_accuracy = '%.5f' % (avg_accuracy)
        user1 = users.objects.get(pk=request.session['User_Id'])
        User_Detail = user1
        return render(request, 'users/user_channel_analysis.html',
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
                       'type1': 'Subscriber',
                       'label1': 'Increments in Subscribers',
                       'label2': 'Prediction of Daily Subscribers Increase For Next Week',
                       'label3': 'Accuracy On Last Week Data Available',
                       'label4': 'Total Subscribers for Last Week Data Available',
                       'label5': 'Predicted Subscribers for Next Week', 'label6': 'History of Previous Predictions'})

    else:
        return HttpResponseRedirect("/Home/")

def bimonthly_subs_channel_analysis(request, channel_id):
    if 'User_Id' in request.session:
        channel_main_data = user_channel_main.objects.get(pk=channel_id)
        channel_sub_data = user_channel_sub.objects.filter(
            channel_id=user_channel_main.objects.get(pk=channel_id)).order_by('-date1')
        channel_sub_data1 = user_channel_sub.objects.filter(
            channel_id=user_channel_main.objects.get(pk=channel_id)).order_by('date1')
        channel_sub_data1 = channel_sub_data1[len(channel_sub_data1) - 15:]
        old_dates = []
        old_views = []
        increse_in_old_views = [0]
        count_1 = 0
        for k in channel_sub_data1:
            if count_1 == 0:
                old_views.append(k.subscriber_count)
                old_dates.append(k.date1)
            else:
                increse_in_old_views.append(k.subscriber_count - old_views[count_1 - 1])
                old_views.append(k.subscriber_count)
                old_dates.append(k.date1)
            count_1 = count_1 + 1
            # print(increse_in_old_views)

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
            avg_accuracy = float(100 - abs((predicted_p2 - actual) / actual) * 100)
            best.append("p2")
        else:
            for i in range(len(old_views)):
                predicted_old_views.append(p1[0] * i + p1[1])
            avg_accuracy = float(100 - abs((predicted_p1 - actual) / actual) * 100)
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
        print(int(predicted_for_next_30[1]), int(predicted_for_next_30[0]), increase_in_predicted_views)
        # #print(len(predicted_dates),len(predicted_for_next_30))
        # for i,j in zip(views,predicted_old_views):
        #    #print(i,j)

        old_views1 = old_views
        increse_in_old_views1 = increse_in_old_views
        predicted_old_views1 = predicted_old_views
        old_dates1 = old_dates
        accuracy_in_old_views1 = accuracy_in_old_views
        # print(accuracy_in_old_views1)
        old_views1 = old_views1[::-1]
        increse_in_old_views1 = increse_in_old_views1[::-1]
        predicted_old_views1 = predicted_old_views1[::-1]
        old_dates1 = old_dates1[::-1]
        accuracy_in_old_views1 = accuracy_in_old_views1[::-1]
        #avg_accuracy = average(accuracy_in_old_views)
        # print('%.5f' % (avg_accuracy))
        avg_accuracy = '%.5f' % (avg_accuracy)
        user1 = users.objects.get(pk=request.session['User_Id'])
        User_Detail = user1
        return render(request, 'users/user_channel_analysis.html',
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
                       'type1': 'Subscriber',
                       'label1': 'Increments in Subscribers',
                       'label2': 'Prediction of Daily Subscribers Increase For Next 15 Days',
                       'label3': 'Accuracy On Last 15 Days Data Available',
                       'label4': 'Total Subscribers for Last 15 Days Data Available',
                       'label5': 'Predicted Subscribers for Next 15 Days', 'label6': 'History of Previous Predictions'})

    else:
        return HttpResponseRedirect("/Home/")

def monthly_subs_channel_analysis(request, channel_id):
    if 'User_Id' in request.session:
        channel_main_data = user_channel_main.objects.get(pk=channel_id)
        channel_sub_data = user_channel_sub.objects.filter(
            channel_id=user_channel_main.objects.get(pk=channel_id)).order_by('-date1')
        channel_sub_data1 = user_channel_sub.objects.filter(
            channel_id=user_channel_main.objects.get(pk=channel_id)).order_by('date1')
        channel_sub_data1 = channel_sub_data1[len(channel_sub_data1) - 30:]
        old_dates = []
        old_views = []
        increse_in_old_views = [0]
        count_1 = 0
        for k in channel_sub_data1:
            if count_1 == 0:
                old_views.append(k.subscriber_count)
                old_dates.append(k.date1)
            else:
                increse_in_old_views.append(k.subscriber_count - old_views[count_1 - 1])
                old_views.append(k.subscriber_count)
                old_dates.append(k.date1)
            count_1 = count_1 + 1
            # print(increse_in_old_views)

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
            avg_accuracy = float(100 - abs((predicted_p2 - actual) / actual) * 100)
            best.append("p2")
        else:
            for i in range(len(old_views)):
                predicted_old_views.append(p1[0] * i + p1[1])
            avg_accuracy = float(100 - abs((predicted_p1 - actual) / actual) * 100)
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
        print(int(predicted_for_next_30[1]), int(predicted_for_next_30[0]), increase_in_predicted_views)
        # #print(len(predicted_dates),len(predicted_for_next_30))
        # for i,j in zip(views,predicted_old_views):
        #    #print(i,j)

        old_views1 = old_views
        increse_in_old_views1 = increse_in_old_views
        predicted_old_views1 = predicted_old_views
        old_dates1 = old_dates
        accuracy_in_old_views1 = accuracy_in_old_views
        # print(accuracy_in_old_views1)
        old_views1 = old_views1[::-1]
        increse_in_old_views1 = increse_in_old_views1[::-1]
        predicted_old_views1 = predicted_old_views1[::-1]
        old_dates1 = old_dates1[::-1]
        accuracy_in_old_views1 = accuracy_in_old_views1[::-1]
        #avg_accuracy = average(accuracy_in_old_views)
        # print('%.5f' % (avg_accuracy))
        avg_accuracy = '%.5f' % (avg_accuracy)
        user1 = users.objects.get(pk=request.session['User_Id'])
        User_Detail = user1
        return render(request, 'users/user_channel_analysis.html',
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
                       'type1': 'Subscriber',
                       'label1': 'Increments in Subscribers',
                       'label2': 'Prediction of Daily Subscribers Increase For Next Month',
                       'label3': 'Accuracy On Last Month Data Available',
                       'label4': 'Total Subscribers for Last Month Data Available',
                       'label5': 'Predicted Subscribers for Next Month', 'label6': 'History of Previous Predictions'})

    else:
        return HttpResponseRedirect("/Home/")

def total_subs_channel_analysis(request, channel_id):
    if 'User_Id' in request.session:
        channel_main_data = user_channel_main.objects.get(pk=channel_id)
        channel_sub_data = user_channel_sub.objects.filter(
            channel_id=user_channel_main.objects.get(pk=channel_id)).order_by('-date1')
        channel_sub_data1 = user_channel_sub.objects.filter(
            channel_id=user_channel_main.objects.get(pk=channel_id)).order_by('date1')
        old_dates = []
        old_views = []
        increse_in_old_views = [0]
        count_1 = 0
        for k in channel_sub_data1:
            if count_1 == 0:
                old_views.append(k.subscriber_count)
                old_dates.append(k.date1)
            else:
                increse_in_old_views.append(k.subscriber_count - old_views[count_1 - 1])
                old_views.append(k.subscriber_count)
                old_dates.append(k.date1)
            count_1 = count_1 + 1
            # print(increse_in_old_views)

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
            avg_accuracy = float(100 - abs((predicted_p2 - actual) / actual) * 100)
            best.append("p2")
        else:
            for i in range(len(old_views)):
                predicted_old_views.append(p1[0] * i + p1[1])
            avg_accuracy = float(100 - abs((predicted_p1 - actual) / actual) * 100)
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
        print(int(predicted_for_next_30[1]), int(predicted_for_next_30[0]), increase_in_predicted_views)
        # #print(len(predicted_dates),len(predicted_for_next_30))
        # for i,j in zip(views,predicted_old_views):
        #    #print(i,j)

        old_views1 = old_views
        increse_in_old_views1 = increse_in_old_views
        predicted_old_views1 = predicted_old_views
        old_dates1 = old_dates
        accuracy_in_old_views1 = accuracy_in_old_views
        # print(accuracy_in_old_views1)
        old_views1 = old_views1[::-1]
        increse_in_old_views1 = increse_in_old_views1[::-1]
        predicted_old_views1 = predicted_old_views1[::-1]
        old_dates1 = old_dates1[::-1]
        accuracy_in_old_views1 = accuracy_in_old_views1[::-1]
        #avg_accuracy = average(accuracy_in_old_views)
        # print('%.5f' % (avg_accuracy))
        avg_accuracy = '%.5f' % (avg_accuracy)
        user1 = users.objects.get(pk=request.session['User_Id'])
        User_Detail = user1
        return render(request, 'users/user_channel_analysis.html',
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
                       'type1': 'Subscriber',
                       'label1': 'Increments in Subscribers',
                       'label2': 'Prediction of Daily Subscribers Increase For Next Month',
                       'label3': 'Accuracy On Total Data Available',
                       'label4': 'Total Subscribers for Total Data Available',
                       'label5': 'Predicted Subscribers for Next Month', 'label6': 'History of Previous Predictions'})

    else:
        return HttpResponseRedirect("/Home/")