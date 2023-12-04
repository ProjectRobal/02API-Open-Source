from django.http import HttpResponseBadRequest,HttpResponse,HttpResponseNotFound
from django.shortcuts import render,redirect
from auth02.models import O2User
from django.contrib.auth.models import Permission
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth.decorators import login_required,permission_required
from django.contrib.auth import authenticate
from domena.settings import MEDIA_URL
import logging

from .models import ProfilePicture,ProjectGroup,CardNode,ToProgramBuffer
from .forms import ProfileImage02Form,Profile02Form
import datetime

import json

@login_required(login_url="/accounts/login")
def program_card(request):
    if request.method != "GET":
        return HttpResponseBadRequest()
    
    if ToProgramBuffer.objects.count()>0:
        
        buffer=ToProgramBuffer.objects.get()

        if datetime.datetime.today().astimezone()-buffer.created_date > datetime.timedelta(days=1):
            buffer.delete()
        else:
            request.session["profile_msg"]="Another card is waitting for programming!"
            return redirect("/webadmin/profile")

    user:O2User=request.user

    cards=CardNode.objects.filter(user=user)

    if not cards.exists():
        request.session["profile_msg"]="No cards defined for a user!"
        return redirect("/webadmin/profile")
    
    buff=ToProgramBuffer(card=cards.first())

    buff.save()

    request.session["profile_msg"]="Card is waiting for programing"

    return redirect("/webadmin/profile")


@login_required(login_url="/accounts/login")
def clear_program_card(request):
    if request.method != "GET":
        return HttpResponseBadRequest()
    
    user:O2User=request.user

    if not user.is_staff:
        return HttpResponse("Unauthorized",'text/html',401)
    
    for buf in ToProgramBuffer.objects.all():
        buf.delete()

    request.session["profile_msg"]="Program buffer is cleared!"

    return redirect("/webadmin/profile")

@login_required(login_url="/accounts/login")
def cards_view(request):
    if request.method != "GET":
        return HttpResponseBadRequest()
    
    in_piwnica:list[CardNode]=CardNode.objects.filter(is_in_basement=True)

    logging.debug("Found "+str(len(in_piwnica))+" people in basement")

    users:list[tuple[O2User,ProfilePicture,list[str]]]=[]

    for piwniczak in in_piwnica:
        try:
            picture=ProfilePicture.objects.get(user=piwniczak.user).image
            picture='{0}/{1}'.format(MEDIA_URL,picture)
        except ProfilePicture.DoesNotExist:
            logging.debug("User "+piwniczak.user.username+" doesn't have profile picture!")
            picture='/static/dummy.png'

        users_groups:list[str]=[group.project_name for group in ProjectGroup.objects.filter(user=piwniczak.user)]

        users.append((piwniczak.user,picture,users_groups))
    
    return render(request,"/app/webadmin/templates/index.html",context={"users":users})

@login_required(login_url="/accounts/login")
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

    return redirect("/webadmin/profile")

@login_required(login_url="/accounts/login")
def logout_from_basement(request):
    if request.method != "GET":
        return HttpResponseBadRequest()
    
    user:O2User=request.user

    cards=CardNode.objects.filter(user=user)

    if not cards.exists():
        request.session["profile_msg"]="No cards defined for a user!"
        return redirect("/webadmin/profile")

    for card in cards:
        card.is_in_basement=False

        card.save()

    request.session["profile_msg"]="User succesfuly loged out from basement!"

    return redirect("/webadmin/profile")

@login_required(login_url="/accounts/login")
def img_set(request):
    if request.method != "POST":
        return HttpResponseBadRequest()
    
    form:ProfileImage02Form=ProfileImage02Form(request.POST,request.FILES)

    if not form.is_valid():
        logging.error(str(form.errors))
        return redirect("/webadmin/profile")   

    user:O2User=request.user

    images=ProfilePicture.objects.filter(user=user)

    # check for existing user image 

    if images.exists():
        logging.debug("Found existing pictures!")

    for img in images:
        img.delete(keep_parents=True)

    clean_data=form.cleaned_data

    if clean_data.get("picture") is None:
        logging.debug("Picture has been removed!")
        return redirect("/webadmin/profile")

    image:ProfilePicture=ProfilePicture(user=user,
                                        image=clean_data.get("picture"))
    
    image.save()

    logging.debug("Picture has been set!")

    return redirect("/webadmin/profile")


@login_required(login_url="/accounts/login")
def update_profile(request):

    if request.method != "POST":
        return HttpResponseBadRequest()
    

    user_form:Profile02Form=Profile02Form(request.POST)

    user:O2User=request.user

    for group in ProjectGroup.objects.filter(user=user):
        if not group.name in user_form["project"].value():
            group.user.remove(user)
            group.save()

    for group in ProjectGroup.objects.filter(name__in=user_form["project"].value()):
        group.user.add(user)
        group.save()

    return redirect("/webadmin/profile")

@login_required(login_url="/accounts/login")
def profile(request):

    if request.method != "GET":
        return HttpResponseBadRequest()
    
    user:O2User=request.user

    groups=ProjectGroup.objects.filter(user=user)

    groups_choosed=[]

    for group in groups:
        groups_choosed.append(group.name)
    
    #logging.debug("Groups choosed: "+str(groups_choosed))

    profile_form:Profile02Form=Profile02Form(initial={
        "username":user.username,
        "email":user.email,
        "first_name":user.first_name,
        "last_name":user.last_name,
        "project":groups_choosed
    })   


    msg=None

    if "profile_msg" in request.session.keys():
        msg=request.session["profile_msg"]
        del request.session["profile_msg"]


    return render(request,"/app/webadmin/templates/profile02.html",context={"img_form":ProfileImage02Form,
                                                                            "profile_form":profile_form,
                                                                            "msg":msg})

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
