from django.http import HttpResponseBadRequest,HttpResponse,HttpResponseNotFound
from django.shortcuts import render,redirect
from auth02.models import O2User
from django.contrib.auth.models import Permission
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth.decorators import login_required,permission_required
from django.contrib.auth import authenticate
from domena.settings import MEDIA_URL
import logging

from .models import ProfilePicture,ProjectGroup,CardNode
from .forms import Register02Form,ProfileImage02Form,Profile02Form
from .apps import WebadminConfig
from django import forms

import json

@login_required(login_url="/login")
def generate_new_card(request):
    if request.method != "GET":
        return HttpResponseBadRequest()
    
    user:O2User=request.user

    try:

        try:

            card:CardNode=CardNode.objects.filter(user=user)

            if len(card)!=0:
                card=card[0]
            else:
                raise CardNode.DoesNotExist
            
            was_in_basement:bool=card.is_in_basement

            card.delete()

            card=CardNode(user=user,is_in_basement=was_in_basement)

            card.save()
    
        except CardNode.DoesNotExist:
        
            card:CardNode=CardNode(user=user)

            card.save()
        
        request.session["profile_msg"]="Cards succesfully regenerated!"

    except Exception as e:
        request.session["profile_msg"]=str(e)

    return redirect("/profile")


@login_required(login_url="/login")
def img_set(request):
    if request.method != "POST":
        return HttpResponseBadRequest()
    
    form:ProfileImage02Form=ProfileImage02Form(request.POST,request.FILES)

    if not form.is_valid():
        logging.error(str(form.errors))
        return redirect("/profile")   

    user:O2User=request.user

    images=ProfilePicture.objects.filter(user=user)

    # check for existing user image 

    if images.exists():
        logging.debug("Found existing pictures!")

    for img in images:
        img.delete(keep_parents=True)

    image:ProfilePicture=ProfilePicture(user=user,
                                        image=form.cleaned_data.get("picture"))
    
    image.save()

    logging.debug("Picture has been set!")

    return redirect("/profile")


@login_required(login_url="/login")
def update_profile(request):

    if request.method != "POST":
        return HttpResponseBadRequest()
    

    user_form:Profile02Form=Profile02Form(request.POST)

    user:O2User=request.user

    if len(user_form["email"].value())!=0:
        user.email=user_form["email"].value()

    if len(user_form["username"].value())!=0:
        user.username=user_form["username"].value()

    if len(user_form["first_name"].value())!=0:
        user.first_name=user_form["first_name"].value()

    if len(user_form["last_name"].value())!=0:
        user.last_name=user_form["last_name"].value()
    if len(user_form["login"].value())!=0:
        user.login=user_form["login"].value()
    
    user.save()

    for group in ProjectGroup.objects.filter(user=user):
        if not group.name in user_form["project"].value():
            group.user.remove(user)
            group.save()

    for group in ProjectGroup.objects.filter(name__in=user_form["project"].value()):
        group.user.add(user)
        group.save()

    return redirect("/profile")

@login_required(login_url="/login")
def profile(request):

    if request.method != "GET":
        return HttpResponseBadRequest()
    
    profile_img=""

    user:O2User=request.user

    groups=ProjectGroup.objects.filter(user=user)

    groups_choosed=[]

    for group in groups:
        groups_choosed.append(group.name)
    
    #logging.debug("Groups choosed: "+str(groups_choosed))

    profile_form:Profile02Form=Profile02Form(initial={
        "login":user.login,
        "username":user.username,
        "email":user.email,
        "first_name":user.first_name,
        "last_name":user.last_name,
        "project":groups_choosed
    })   


    try:

        pic=ProfilePicture.objects.get(user=user)
        profile_img='{0}/{1}'.format(MEDIA_URL,pic.image)
        
    except ProfilePicture.DoesNotExist:
        profile_img="/static/dummy.png"

    msg=None

    if "profile_msg" in request.session.keys():
        msg=request.session["profile_msg"]
        del request.session["profile_msg"]


    return render(request,"/app/webadmin/templates/profile02.html",context={"img_form":ProfileImage02Form,
                                                                            "profile_form":profile_form,
                                                                            "profile_img":profile_img,
                                                                            "msg":msg})

def reg(request):
    
    if request.method != "POST":
        return HttpResponseBadRequest()
    
    register=Register02Form(request.POST)

    if not register.is_valid():
        request.session["login_error"]=register.errors
        return redirect("/register")

    register=register.cleaned_data

    try:

        O2User.objects.get(username=register["username"])
        #request.session["login_error"]=register.errors
        return redirect("/login?user_exists=1")

    except O2User.DoesNotExist:

        user:O2User=O2User.objects.create_user(
            username=register["username"],
            first_name=register["first_name"],
            last_name=register["last_name"],
            email=register["email"],
            password=register["password"],
            login=register["login"]
        )

        cards_view=Permission.objects.get(codename="cards_view")
        device_view=Permission.objects.get(codename="device_view")
        plugin_view=Permission.objects.get(codename="plugin_view")

        user.user_permissions.add(cards_view)
        user.user_permissions.add(device_view)
        user.user_permissions.add(plugin_view)

        user.save()

    for group in ProjectGroup.objects.filter(name__in=register["project"]):
        group.user.add(user)
        group.save()


    user_card=CardNode(user=user)

    user_card.save()

    return redirect("/login?login_success=1")

def reg_form(request):

    if request.method != "GET":
        return HttpResponseBadRequest()
    
    msg=None

    if "login_error" in request.session.keys():
        msg=""
        for error in request.session["login_error"].values():
            msg+=str(error[0])+" \n"
        del request.session["login_error"]

    return render(request,"/app/webadmin/templates/register02form.html",context={"form":Register02Form,"msg":msg})


def get_id(request):
    if request.method != "GET":
        return HttpResponseNotFound()
    
    #logging.debug("Body: "+str(request.read()))
    
    body=json.load(request)
 
    if not "username" in body.keys() or not "password" in body.keys():
        logging.debug("No username or password filds")
        return HttpResponseBadRequest()
    
    user:O2User=authenticate(username=body["username"],password=body["password"])

    if user is None:
        logging.debug("No specified user has been found")
        return HttpResponseBadRequest("User creditentials are wrong")
    
    cards=CardNode.objects.filter(user=user).all()

    output=[]

    if cards.exists():
        for card in cards.values("key","is_in_basement"):
            output.append(card)

    return HttpResponse(json.dumps(output,cls=DjangoJSONEncoder),content_type="application/json")
