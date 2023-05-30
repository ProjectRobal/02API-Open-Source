from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.

def homePage(request):
    '''placeholder page'''
    
    return render(request,"/app/devices/templates/index.html")

    return HttpResponse("Coming soon :)",content_type="text/html")


