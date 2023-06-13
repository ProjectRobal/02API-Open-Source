from django.http import HttpResponseBadRequest
from django.shortcuts import render,redirect
from django.contrib.auth.models import User

from .forms import Register02Form

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

