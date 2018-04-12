from django.http import HttpResponseRedirect
from django.shortcuts import render

# Create your views here.
from django.urls import reverse
from channel.models import channel_main
from users.models import users
from Home.models import contact_us_form

def Home(request):
    channels_list = channel_main.objects.all().order_by('pk')[:4]
    if 'User_Id' in request.session:
        return HttpResponseRedirect('/users/')
    else:
        return render(request, 'Home/Home.html', {'User_Detail': '','Channel_List':channels_list})

def Demo(request):
    return render(request, 'Home/test.html')

def contact_us(request):
    if request.method == 'POST':
        fname = request.POST.get('form_name')
        lname = request.POST.get('form_lastname')
        email = request.POST.get('form_email')
        message = request.POST.get('form_message')
        contact_obj = contact_us_form(first_name=fname,last_name=lname,email=email,message=message)
        contact_obj.save()
        return HttpResponseRedirect(reverse(contact_us))
    else:
        if 'User_Id' in request.session:
            user1 = users.objects.get(pk=request.session['User_Id'])
            User_Detail = user1
        else:
            User_Detail = ''
        #return HttpResponseRedirect('/Home/contact_us/')
        return render(request,'Home/contact_us.html',{'User_Detail': User_Detail,})

def about_us(request):
    return render(request,'Home/about_us.html')
