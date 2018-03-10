from django.shortcuts import render

# Create your views here.
def Home(request):
	print("changes made by Jay");
	print("another change made by Jay");
    return render(request, 'Home/Home.html')