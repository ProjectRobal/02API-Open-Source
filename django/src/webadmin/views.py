from django.http import HttpResponse,HttpResponseBadRequest,HttpResponseNotFound
from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.models import User

from .forms import LoginForm,Register02Form

def reg(request):
    
    if request.method != "POST":
        return HttpResponseBadRequest()
    
    register=Register02Form(request.POST)

    try:

        User.objects.get(username=register["username"].value())

        return redirect('/register')

    except User.DoesNotExist:

        user=User.objects.create_user(
            username=register["username"].value(),
            first_name=register["first_name"].value(),
            last_name=register["last_name"].value(),
            email=register["email"].value(),
            password=register["password"].value()
        )

    return redirect("/login?log_success=1")

def reg_form(request):

    if request.method != "GET":
        return HttpResponseBadRequest()

    return render(request,"/app/webadmin/templates/register02form.html",context={"form":Register02Form})

def perm_fail(request):

    return render(request,"/app/webadmin/templates/permfail.html")

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

    return render(request,"/app/webadmin/templates/loginform.html",context={"login_success":login_success,"bad_login":bad_login,"perm_fail":perm_fail,"form":LoginForm})

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