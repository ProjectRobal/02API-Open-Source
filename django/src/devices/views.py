from django.http import HttpResponse,HttpResponseBadRequest,HttpResponseNotFound
from django.shortcuts import render,redirect
from .models import Device
from mqtt.models import Topic
from nodeacl.models import NodeACL
from common.acess_levels import Access
from nodes.models import PublicNodes
from django.forms.models import model_to_dict
from django.contrib.auth.decorators import login_required,permission_required
from domena.home import entries
from domena.plugins import PLUGINS
from .plugin_loader import parse_plugin,PluginInfo,add_plugin,PLUGIN_TMP_FILE,scan_for_plugin
from .forms import PluginFileForm
import os

import logging

# Create your views here.

class TopicInterface:
    def __init__(self,node) -> None:
        self.access=Access(node.access_level).name
        self.topic=node.topic
        self.node=node


@login_required(login_url="/login")
@permission_required("devices.plugin_add",login_url="/permf")
def plugin_add(request):

    return render(request,"/app/devices/templates/add_plugin.html",context={"plugin_form":PluginFileForm})

@login_required(login_url="/login")
@permission_required("devices.plugin_add",login_url="/permf")
def ploader(request):
    '''A function to load plugins'''

    if request.method != 'POST':
        return HttpResponseNotFound()
    
    form:PluginFileForm=PluginFileForm(request.POST,request.FILES)

    if not form.is_valid():
        return redirect("/plugin_add")

    file=form.cleaned_data.get('file')

    #save as temporary

    if not os.path.exists("tmp"):
        os.mkdir("tmp")

    with open(PLUGIN_TMP_FILE,"wb+") as pfile:
        for chunk in file.chunks():
            pfile.write(chunk)
    
    # reset django on success
    if add_plugin():
        pass

    return redirect("/devs")

def home_page(request,name=None):

    return render(request,"/app/devices/templates/home.html",context={"name":name,"blocks":entries})

@login_required(login_url="/login")
def rat(request):

    return render(request,"/app/devices/templates/rat.html")

@login_required(login_url="/login")
@permission_required("devices.device_view",login_url="/permf")
def node_list(request,name):
    
    if request.method != 'GET':
        return HttpResponseNotFound()
    
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

    plugins:list[PluginInfo]=[]

    for plugin in scan_for_plugin():
        plug=parse_plugin(plugin)
        if plug is not None:
            plugins.append(plug)

    return render(request,"/app/devices/templates/index.html",context={"devices":devices,"plugins":plugins})

@login_required(login_url="/login")
@permission_required("devices.device_view",login_url="/permf")
def device_page(request,name):
    '''page to display informations about device'''

    if request.method != 'GET':
        return HttpResponseNotFound()
    
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