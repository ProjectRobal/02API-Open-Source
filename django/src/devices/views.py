from django.http import HttpResponse,HttpResponseBadRequest,HttpResponseNotFound
from django.shortcuts import render
from .models import Device
from mqtt.models import Topic
from nodeacl.models import NodeACL
from common.acess_levels import Access
from nodes.models import PublicNodes
from django.forms.models import model_to_dict
from django.contrib.auth.decorators import login_required,permission_required
from domena.home import entries

# Create your views here.

class TopicInterface:
    def __init__(self,node) -> None:
        self.access=Access(node.access_level).name
        self.topic=node.topic
        self.node=node



def home_page(request,name=None):

    return render(request,"/app/devices/templates/home.html",context={"name":name,"blocks":entries})

@login_required(login_url="/login")
def rat(request):

    return render(request,"/app/devices/templates/rat.html")

@login_required(login_url="/login")
@permission_required("devices.device_view",login_url="/permf")
def node_list(request,name):
    
    if request.method != 'GET':
        return HttpResponseBadRequest()
    
    node=PublicNodes.get_obj(name)

    if node is None:
        return HttpResponseNotFound()

    node_list=node.objects.all()

    list_nodes=[]

    for node in node_list:
        params=[]
        dict=model_to_dict(node)
        for key in dict.keys():
            params.append((key,str(dict[key])))
        list_nodes.append(params)
    
    return render(request,"/app/devices/templates/list_nodes.html",context={"nodes":list_nodes,"name":name})

@login_required(login_url="/login")
@permission_required("devices.device_view",login_url="/permf")
def devsPage(request):
    '''placeholder page'''

    devices=Device.objects.all()

    return render(request,"/app/devices/templates/index.html",context={"devices":devices})

@login_required(login_url="/login")
@permission_required("devices.device_view",login_url="/permf")
def device_page(request,name):
    '''page to display informations about device'''

    if request.method != 'GET':
        return HttpResponseBadRequest()
    
    try:
    
        device=Device.objects.get(name=name)
        last_login=str(device.last_login_date)

        nodesacl=NodeACL.objects.filter(device=device.id)

        node_list=[]
        
        for node in nodesacl:
            node_list.append(TopicInterface(node))

    except Device.DoesNotExist:
        return HttpResponseNotFound()
    
    return render(request,"/app/devices/templates/device.html",context={"device":device,"login_date":last_login,"nodesacl":node_list})

@login_required(login_url="/login")
def twingoPage(request):
    '''twoja stara'''

    return render(request,"/app/devices/templates/twingo.html")