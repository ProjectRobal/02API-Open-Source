from django.http import HttpResponseBadRequest,HttpResponse,HttpResponseNotFound
from django.shortcuts import render,redirect
from auth02.models import O2User
from django.contrib.auth.decorators import login_required
import logging

from lej.models import LejUserRecord
import datetime

import json

# Create your views here.

# for testings
# @login_required(login_url="/accounts/login")
def ranking_view(request):
    if request.method != "GET":
        return HttpResponseBadRequest()
    
    records = LejUserRecord.objects.all().order_by('miliseconds')
    
    record_list = []
    
    for record in records:
        
        seconds = int(record.miliseconds/1000)
        
        miliseconds = record.miliseconds - 1000*seconds
        
        record_list.append({
            "name":record.name,
            "miliseconds":miliseconds,
            "seconds":seconds,
        })
    
    return render(request,"/app/lej/templates/ranking.html",context={"records":record_list})