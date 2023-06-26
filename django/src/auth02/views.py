from django.http import HttpResponse,HttpResponseBadRequest,HttpResponseNotFound
from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login,logout

from .forms import LoginForm
# Create your views here.


def perm_fail(request):

    return render(request,"/app/auth02/templates/permfail.html")

def login_form(request):

    if request.method != "GET":
        return HttpResponseBadRequest()
    

    msg=None

    if "bad_login" in request.GET:
        msg="Bad login!"

    if "perm_fail" in request.GET:
        msg="Permision failed!"
    
    if "login_success" in request.GET:
        msg="User created succesfully!"

    if "user_exists" in request.GET:
        msg="User aleardy exits!"

    return render(request,"/app/auth02/templates/loginform.html",context={"msg":msg,"form":LoginForm})

def auth(request):

    if request.method != "POST":
        return HttpResponseBadRequest()
    
    logout(request)

    loginData=LoginForm(request.POST)

    if not loginData.is_valid():
        return redirect("/login?bad_login=1")

    user=authenticate(request,username=loginData["user"].value(),password=loginData["pwd"].value())

    if user is not None:
        login(request,user)
        return redirect("/")
    else:
        return redirect("/login?bad_login=1")
    

def unauth(request):
    logout(request)

    return redirect("/login/")