from django.http import HttpResponseBadRequest,HttpResponse,HttpResponseNotFound
from django.shortcuts import render,redirect
from auth02.models import O2User
from django.contrib.auth.decorators import login_required
import logging

import random

from lej.models import LejUserRecord

import json

def get_last_update()->float:
    if LejUserRecord.objects.count() > 0:
        return LejUserRecord.objects.all().order_by("-modified_date")[0].modified_date.timestamp()
    
    return 0.0

# Create your views here.

def check_for_update(request):
    if request.method != "GET":
        return HttpResponseBadRequest()
    
    last_update_time = get_last_update()
    
    output = {
        "time":last_update_time
    }
    
    return HttpResponse(json.dumps(output),content_type="application/json")

# for testings
# @login_required(login_url="/accounts/login")
def ranking_view(request):
    if request.method != "GET":
        return HttpResponseBadRequest()
    
    
    
    records = LejUserRecord.objects.all().order_by('miliseconds')
    
    record_list = []
        
    if "seed" in request.GET:
        seed = int(request.GET["seed"])
    else:
        seed = random.randint(0,100)
        
    if "seed1" in request.GET:
        seed1 = int(request.GET["seed1"])
    else:
        seed1 = random.randint(0,100)
        
    if "seed2" in request.GET:
        seed2 = int(request.GET["seed2"])
    else:
        seed2 = random.randint(0,100)
        
    if "seedm" in request.GET:
        seedm = int(request.GET["seedm"])
    else:
        seedm = random.randint(0,100)
        
    if "seedc" in request.GET:
        seedc = int(request.GET["seedc"])
    else:
        seedc = random.randint(0,100)
        
    if "seede" in request.GET:
        seede = int(request.GET["seede"])
    else:
        seede = random.randint(0,100)
        
    if "seedb" in request.GET:
        seedb = int(request.GET["seedb"])
    else:
        seedb = random.randint(0,100)
        
    helper = random.randint(0,1000)
    
    last_update_time = get_last_update()
    
    logging.debug("Seed: {}".format(seed))
    
    for record in records:
        
        seconds = int(record.miliseconds/1000)
        
        miliseconds = record.miliseconds - 1000*seconds
        
        record_list.append({
            "name":record.name,
            "miliseconds":miliseconds,
            "seconds":seconds,
        })
    
    return render(request,"/app/lej/templates/ranking.html",context={"records":record_list,"seed":seed,"seed_1":seed1,"seed_2":seed2,"seedm":seedm,"seedc":seedc,"seede":seede,"seedb":seedb,"update_time":last_update_time,"second":helper})