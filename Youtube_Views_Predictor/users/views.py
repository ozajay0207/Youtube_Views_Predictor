from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from users.models import users
from Crypto.Hash import SHA256
# Create your views here.

def DashBoard(request):
    if 'User_Id' in request.session:
        user1 = users.objects.get(pk=request.session['User_Id'])
        User_Detail = user1
        return render(request, 'users/Users_Dashboard.html', {'User_Detail':User_Detail})
    else:
        return HttpResponseRedirect('/Home/')


def Sign_Up(request):
    if 'User_Id' in request.session:
        user1 = users.objects.get(pk=request.session['User_Id'])
        User_Detail = user1
        return render(request, 'users/Users_Dashboard.html', {'User_Detail':User_Detail})
    else:
        if request.method == 'POST':
            Email=request.POST.get('val-email')
            Display_Name=request.POST.get('val-display-name')
            Password=request.POST.get('val-password')
            Password_Hash=SHA256.new(Password.encode('utf-8')).hexdigest()
            user1= users(Email=Email,Display_Name=Display_Name,Password=Password_Hash)
            user1.save()
            request.session['User_Id']=user1.id

            return HttpResponseRedirect('/users/')
            #User_Detail=user1
            #return render(request, 'users/Users_Dashboard.html', {'User_Detail':User_Detail})
        else:
            return HttpResponseRedirect('/Home/')

def Sign_In(request):
    if 'User_Id' in request.session:
        return HttpResponseRedirect('/users/')
        #user1 = users.objects.get(pk=request.session['User_Id'])
        #User_Detail = user1
        #return render(request, 'users/Users_Dashboard.html', {'User_Detail':User_Detail})
    else:
        if request.method == 'POST':
            Email = request.POST.get('val-email')
            Password = request.POST.get('val-password')
            Password_Hash = SHA256.new(Password.encode('utf-8')).hexdigest()
            try:
                user1=users.objects.get(Email=Email,Password=Password_Hash)
                request.session['User_Id']=user1.id
                return HttpResponseRedirect('/users/')
                #User_Detail = user1
                #return render(request, 'users/Users_Dashboard.html', {'User_Detail': User_Detail})
            except:
                return HttpResponseRedirect('/Home/')
        else:
            return HttpResponseRedirect('/Home/')
def Sign_Out(request):
    del request.session['User_Id']
    return HttpResponseRedirect('/Home/')

def login(request):
    return render(request,'users/Login.html')

def register(request):
    return render(request,'users/Register.html')

def validate_email(request):
    print("validate")
    Email=request.GET.get('val-email')
    data = {
        'is_taken': users.objects.get(Email__iexact=Email).exists()
    }
    if not data['is_taken']:
        data['error_message'] = 'A user with given Email is not exists.'
    return JsonResponse(data)

def validate_display_name(request):
    if request.method == "POST":
        query = request.POST.get('val-display-name')
        print(query)
        if query == '':
            return render(request, 'users/search_result.html', {'data': 'None'})
        else:
            data = users.objects.get(Display_Name=query)
    else:
        query = ''
        data = {}

    return render(request, 'users/search_result.html', {'data': data})
