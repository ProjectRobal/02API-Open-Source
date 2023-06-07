from django.http import HttpResponse,HttpResponseBadRequest,HttpResponseNotFound
from django.shortcuts import render

def login_form(request):
    
    return render(request,"/app/webadmin/templates/loginform.html")
