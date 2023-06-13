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
    
    bad_login=False
    perm_fail=False
    login_success=False

    if "bad_login" in request.GET:
        bad_login=True

    if "perm_fail" in request.GET:
        perm_fail=True
    
    if "login_success" in request.GET:
        login_success=True

    return render(request,"/app/auth02/templates/loginform.html",context={"login_success":login_success,"bad_login":bad_login,"perm_fail":perm_fail,"form":LoginForm})

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