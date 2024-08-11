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
from domena.settings import PLUGINS_LIST
import domena.plugins as plugins_func
from services.models import ServiceProfile
import datetime


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

            check=Topic.objects.get(path="/"+path+"/")

        except Topic.DoesNotExist:
            logging.debug("Topic not found")
            return HttpResponse(str(FetchResult(-12,"Topic not found","")),content_type="application/json")
    
        logging.debug("Found command: "+cmd)
        logging.debug("Check node: "+check.node)

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

@login_required(login_url="/accounts/login/")
#@permission_required("devices.device_add",login_url="/permf")
def node_view(request,name:str):

    if request.method != "GET":   
        return HttpResponseBadRequest()
    
    obj=PublicNodes.get_obj(name)

    if obj is None:
        logging.error("Not found node with name: "+str(name))
        return HttpResponseNotFound()
    
    # we exclude fields about creation date and modification date
    params_list_count:list=[x.name for x in obj._meta.get_fields()]
    logging.debug("Got "+str(params_list_count))

    for rem in ["created_date","modified_date","uuid"]:
        params_list_count.remove(rem)
    
    return render(request,"/app/devices/templates/nodes_view.html",context={"node":name,"app_name":obj.__name__,"node_params":params_list_count})
    
    


@login_required(login_url="/accounts/login/")
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

@login_required(login_url="/accounts/login/")
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

@login_required(login_url="/accounts/login/")
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


    
@login_required(login_url="/accounts/login/")
@permission_required("devices.plugin_add",login_url="/permf")
def plugin_add(request):

    return render(request,"/app/devices/templates/add_plugin.html",context={"plugin_form":PluginFileForm})

@login_required(login_url="/accounts/login/")
@permission_required("devices.device_add",login_url="/permf")
def device_add(request):

    return render(request,"/app/devices/templates/add_device.html",context={"form":DeviceFileForm})

@login_required(login_url="/accounts/login/")
def plugin_show(request,name):

    return render(request,"/app/devices/templates/show_plugin.html",context={"plugin":parse_plugin(name)})

@login_required(login_url="/accounts/login/")
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


@login_required(login_url="/accounts/login/")
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

@login_required(login_url="/accounts/login/")
def rat(request):

    return render(request,"/app/devices/templates/rat.html")

@login_required(login_url="/accounts/login/")
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

@login_required(login_url="/accounts/login/")
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

@login_required(login_url="/accounts/login/")
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

@login_required(login_url="/accounts/login/")
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

def device_info(request,uuid:str):
    '''page to list devices installed on app'''

    if request.method != 'GET':
        return HttpResponseNotFound()
    
    
    try:
        
        device = Device.objects.get(uuid=uuid)
        
    except Device.DoesNotExist:
        logging.debug(f"Device with {uuid} not found")
        return HttpResponseNotFound()
    
    # list important informations
    
    logging.debug(f"Found device with {uuid}")
    
    device_info = {
        "uuid":uuid,
        "name":device.name,
        "installation_date":device.created_date,
        "version":f"{device.major_version}.{device.minor_version}.{device.patch_version}"
    }
    
    nodesacl=NodeACL.objects.filter(device=device.uuid)

    node_list=[]
        
    for node in nodesacl:
        node_list.append({
            "path":node.topic.path,
            "access":Access(node.access_level).name,
            "name":node.topic.node,
        })

    return render(request,"/app/devices/templates/device_info.html",context={"device":device_info,"nodes":node_list})

def plugin_list(request):
    '''page to list plugins installed on app'''

    if request.method != 'GET':
        return HttpResponseNotFound()
    
    plugins = PLUGINS_LIST
    
    
    if "search" in request.GET:
        keyword = request.GET["search"]
        logging.debug(f"Got keyword: {keyword}")
        
        n_plugins = []
        
        for plugin in plugins:
            meta:dict = plugins_func.get_meta(plugin)
            if meta["name"].lower().find(keyword) != -1:
                n_plugins.append(plugin)
                
        plugins = n_plugins
        
    
    # list important informations
    
    logging.debug(f"Found {len(plugins)} plugins")
    
    plugin_list = []
    
    for plugin in plugins:
        meta:dict = plugins_func.get_meta(plugin)
        plugin_list.append({
            "name":meta["name"],
            "app_name":plugin
        })
    
    return render(request,"/app/devices/templates/list_plugins.html",context={"plugins_list":plugin_list})

def plugin_info(request,name:str):
    '''page to list plugins installed on app'''

    if request.method != 'GET':
        return HttpResponseNotFound()
            
    if not name in PLUGINS_LIST:
        return HttpResponseNotFound()
        
    meta:dict = plugins_func.get_meta(name)
    
    plugin_info = {
        "name":meta["name"],
        "author":meta["author"],
        "installation_date":datetime.datetime.strptime(meta["installation_date"], "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d %H:%M:%S"),
        "version":meta["version"],
        "app_name":name
    }
    
    # list important informations
    
    logging.debug(f"Found plugins with name {name}")
            
    return render(request,"/app/devices/templates/plugin_info.html",context={"plugin":plugin_info})

def serv_list(request):
    '''page to list devices installed on app'''

    if request.method != 'GET':
        return HttpResponseNotFound()
    
    
    if "search" in request.GET:
        keyword = request.GET["search"]
        logging.debug(f"Got keyword: {keyword}")
        servs = ServiceProfile.objects.filter(name__contains=keyword)
    else:
        servs = ServiceProfile.objects.all()
    
    # list important informations
    
    logging.debug(f"Found {len(servs)} services")
    
    servs_list = []
    
    for serv in servs:
        servs_list.append({
            "name":serv.name,
            "id":serv.uuid
        })
    
    return render(request,"/app/devices/templates/list_serv.html",context={"serv_list":servs_list})

def serv_info(request,uuid:str):
    '''page to list services installed on app'''

    if request.method != 'GET':
        return HttpResponseNotFound()
    
        
    try:
        
        serv = ServiceProfile.objects.get(uuid=uuid)
        
    except ServiceProfile.DoesNotExist:
        return HttpResponseNotFound()
    
    # list important informations
    
    logging.debug(f"Found services with uuid: {uuid}")
        
    serv_info = {
        "name":serv.name,
        "node":serv.node_name
    }
    
    return render(request,"/app/devices/templates/serv_info.html",context={"serv":serv_info})

def list_node(request):
    '''page to list devices installed on app'''

    if request.method != 'GET':
        return HttpResponseNotFound()
    
    nodes = PublicNodes.get_nodes_list()
    
    if "search" in request.GET:
        keyword = request.GET["search"]
        logging.debug(f"Got keyword: {keyword}")
        
        n_nodes = []
        
        for node in nodes:
            if node[1].lower().find(keyword) != -1:
                n_nodes.append(node)     
        
        nodes = n_nodes   
    
    # list important informations
    
    logging.debug(f"Found {len(nodes)} nodes")
    
    node_list = []
    
    for node in nodes:
        node_list.append({
            "name":node[0],
            "node_name":node[1]
        })
    
    return render(request,"/app/devices/templates/node_list.html",context={"node_list":node_list})