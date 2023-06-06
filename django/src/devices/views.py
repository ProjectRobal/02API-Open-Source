from django.http import HttpResponse,HttpResponseBadRequest,HttpResponseNotFound
from django.shortcuts import render
from .models import Device
from mqtt.models import Topic
from nodeacl.models import NodeACL

# Create your views here.

def homePage(request):
    '''placeholder page'''

    devices=Device.objects.all()

    return render(request,"/app/devices/templates/index.html",context={"devices":devices})

def device_page(request,name):
    '''page to display informations about device'''

    if request.method != 'GET':
        return HttpResponseBadRequest()
    
    try:
    
        device=Device.objects.get(name=name)
        last_login=str(device.last_login_date)

        nodesacl=NodeACL.objects.filter(device=device.id)

        topics=[]

        for nodeacl in nodesacl:
            topics.append(nodeacl.topic)

    except Device.DoesNotExist:
        return HttpResponseNotFound()
    
    return render(request,"/app/devices/templates/device.html",context={"device":device,"login_date":last_login,"topics":topics})

def twingoPage(request):
    '''twoja stara'''

    return render(request,"/app/devices/templates/twingo.html")