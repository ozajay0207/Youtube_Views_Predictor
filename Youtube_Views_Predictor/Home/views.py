from django.shortcuts import render

# Create your views here.
from users.models import users


def Home(request):
    if 'User_Id' in request.session:
        user1 = users.objects.get(pk=request.session['User_Id'])
        User_Detail = user1
        return render(request, 'Home/Home.html',{'User_Detail':User_Detail})
    else:
        return render(request, 'Home/Home.html', {'User_Detail': ''})

def Demo(request):
    return render(request, 'Home/test.html')