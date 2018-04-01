from django.shortcuts import render

# Create your views here.
from channel.models import channel_main
from users.models import users


def Home(request):
    channels_list = channel_main.objects.all().order_by('pk')[:4]
    if 'User_Id' in request.session:
        user1 = users.objects.get(pk=request.session['User_Id'])
        User_Detail = user1
        return render(request, 'Home/Home.html',{'User_Detail':User_Detail,'Channel_List':channels_list})
    else:
        return render(request, 'Home/Home.html', {'User_Detail': '','Channel_List':channels_list})

def Demo(request):
    return render(request, 'Home/test.html')