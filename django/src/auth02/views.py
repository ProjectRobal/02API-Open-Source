from django.http import HttpResponse,HttpResponseBadRequest,HttpResponseNotFound
from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login,logout
from domena.settings import DEFAULT_SESSION_TIME
from .models import O2User
import time
import logging
import json

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

    if "login_error" in request.session.keys():
        msg=str(list(request.session["login_error"].values())[-1][0])
        del request.session["login_error"]


    return render(request,"/app/auth02/templates/loginform.html",context={"msg":msg,"form":LoginForm})

def auth(request):

    if request.method != "POST":
        return HttpResponseBadRequest()
    
    logout(request)

    loginData=LoginForm(request.POST)

    if not loginData.is_valid():
        return redirect("/login?bad_login=1")

    user:O2User=authenticate(request,username=loginData["user"].value(),password=loginData["pwd"].value())

    if user is not None:
        login(request,user)
        # defines a time after session expired
        request.session["session_time"]=DEFAULT_SESSION_TIME
        request.session['last_touch'] = int(time.time())
        logging.debug("User with username: "+user.get_username()+" logged with session time: "+str(request.session["session_time"]))
        return redirect("/")
    else:
        return redirect("/login?bad_login=1")
    

def unauth(request):
    logout(request)

    return redirect("/login/")