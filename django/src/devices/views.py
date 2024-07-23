from django.http import HttpResponse,HttpResponseBadRequest,HttpResponseNotFound,HttpResponseServerError
from django.shortcuts import render,redirect
from .models import Device
from mqtt.models import Topic
from nodeacl.models import NodeACL
from common.acess_levels import Access
from nodes.models import PublicNodes
from django.forms.models import model_to_dict
from django.contrib.auth.decorators import login_required,permission_required
from domena.home import entries
from domena.plugins import PLUGINS,scan_for_plugin
from importer.plugin_loader import parse_plugin,PluginInfo,add_plugin,PLUGIN_TMP_FILE,remove_plugin
from importer.device_loader import gen_device,remove_device,purge_device,DEVICE_TMP_FILE
from .forms import PluginFileForm,DeviceFileForm
import os
import json
from common.fetch_api import Fetch,FetchResult

import logging

# Create your views here.

class TopicInterface:
    def __init__(self,node) -> None:
        self.access=Access(node.access_level).name
        self.topic=node.topic
        self.node=node

def api(request,path):
    if request.method!="GET":
        return HttpResponseNotFound()
    
    paths=path.rpartition("/")

    cmd=paths[2]
    path=paths[0]
    
    try:
    
        logging.info("Got API request through HTTP")

        logging.debug("Topic: "+path)

        try:

            check=Topic.objects.get(path="/"+path)

        except Topic.DoesNotExist:
            logging.debug("Topic not found")
            return HttpResponse(str(FetchResult(-12,"Topic not found","")),content_type="application/json")
    
        logging.debug("Found command: "+cmd)

        body=json.load(request)

        logging.debug("Body: "+str(json.dumps(body)))

        key=None

        if "key" in body:
               key=body["key"]

        if "data" in body:
               body=body["data"]
        else:
               body={}
    

        fetch=Fetch(key,PublicNodes.get_obj(check.node),check)

        result=fetch.match(cmd,body)

        logging.debug("HTTP API result: "+str(result))

        if key is not None:

            return HttpResponse(str(result),content_type="application/json")
        else:
            logging.debug("No key or output provided!")

        return HttpResponse(str(FetchResult(-12,"Bad request","")),content_type="application/json")
    
    except Exception as e:
        logging.error("I się wywalił")
        logging.error(str(e))
        return HttpResponse(str(FetchResult(-12,"Server error!","")),content_type="application/json")

@login_required(login_url="/login")
@permission_required("devices.device_rm",login_url="/permf")
def device_rm(request):

    if request.method == "POST":   
        
        data=json.loads(request.body)
    
        logging.debug("Device name: "+data["app"])

        if remove_device(data["app"]):
            logging.debug("Device "+data["app"]+" has been removed")
        else:
            logging.debug("Device has not been found")

        return redirect("/devs")
    
    return HttpResponseBadRequest()

@login_required(login_url="/login")
@permission_required("devices.device_rm",login_url="/permf")
def device_purge(request):

    if request.method == "POST":   
        
        data=json.loads(request.body)
    
        logging.debug("Device name: "+data["dev"])

        if purge_device(data["dev"]):
            logging.debug("Device "+data["dev"]+" and it's topics and acl rules have been removed")
        else:
            logging.debug("Device has not been found")

        return redirect("/devs")
    
    return HttpResponseBadRequest()

@login_required(login_url="/login")
@permission_required("devices.plugin_rm",login_url="/permf")
def plugin_rm(request):

    if request.method == "POST":   
        
        data=json.loads(request.body)
    
        logging.debug("app name: "+data["app"])

        if remove_plugin(data["app"]):
            logging.debug("Plugin "+data["app"]+" has been removed")
        else:
            logging.debug("Plugin has not been found")

        return redirect("/devs")
    
    return HttpResponseBadRequest()


    
@login_required(login_url="/login")
@permission_required("devices.plugin_add",login_url="/permf")
def plugin_add(request):

    return render(request,"/app/devices/templates/add_plugin.html",context={"plugin_form":PluginFileForm})

@login_required(login_url="/login")
@permission_required("devices.device_add",login_url="/permf")
def device_add(request):

    return render(request,"/app/devices/templates/add_device.html",context={"form":DeviceFileForm})

@login_required(login_url="/login")
def plugin_show(request,name):

    return render(request,"/app/devices/templates/show_plugin.html",context={"plugin":parse_plugin(name)})

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


@login_required(login_url="/login")
@permission_required("devices.device_add",login_url="/permf")
def devloader(request):
    '''A function to load plugins'''

    if request.method != 'POST':
        return HttpResponseNotFound()
    
    form:DeviceFileForm=DeviceFileForm(request.POST,request.FILES)

    if not form.is_valid():
        return redirect("/device_add")

    file=form.cleaned_data.get('file')

    #save as temporary

    if not os.path.exists("tmp"):
        os.mkdir("tmp")

    with open(DEVICE_TMP_FILE,"wb+") as pfile:
        for chunk in file.chunks():
            pfile.write(chunk)
    
    # reset django on success
    res=gen_device()
    if res[0]:
        os.system("python3 app/manage.py makemigration")
        os.system("python3 app/manage.py migrate")

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
@permission_required(["devices.device_view","devices.plugin_view"],login_url="/permf")
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

        nodesacl=NodeACL.objects.filter(device=device.uuid)

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


def device_list(request):
    '''page to list devices installed on app'''

    if request.method != 'GET':
        return HttpResponseNotFound()
    
    
    if "search" in request.GET:
        keyword = request.GET["search"]
        logging.debug(f"Got keyword: {keyword}")
        devices = Device.objects.filter(name__contains=keyword)
    else:
        devices = Device.objects.all()
    
    # list important informations
    
    logging.debug(f"Found {len(devices)} devices")
    
    device_list = []
    
    for device in devices:
        device_list.append({
            "name":device.name,
            "status":device.status,
            "id":device.uuid
        })
    
    return render(request,"/app/devices/templates/list_device.html",context={"devices_list":device_list})
