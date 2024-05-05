'''
A script that loads plugins

Every plugins has it's own meta file called meta.json

example meta.json:

{
    "name":"Cards web manager",
    "exec_name":"card_bot.py",
    "":""
}

'''

import datetime
import os
from collections import namedtuple
import json
import gzip
import shutil
import logging

from domena.settings import SERVER_VERSION,PLUGINS_LIST
from domena.plugins import scan_for_plugin

from common.utils import compare_versions,version_to_number

from django.core.serializers.json import DjangoJSONEncoder
from services.models import ServiceProfile
from services.apps import SERVICE_IMPORT_PATH,SERVICE_UPLOAD_PATH
from nodes.models import PublicNodes


SERVICE_TMP_FILE="tmp/service.tmp"

SERVICE_TMP_ARCHIVE="tmp/service/unpacked"

# zero two service extension
PLUGIN_ARCHIVE_EXTENSION="zts"

class ServiceInfo:
    name:str
    exec_name:str
    node:str
    version:str



def clean_temporary():
    shutil.rmtree('tmp', ignore_errors=True)

def remove_service(id:str)->bool:
    
    try:
        
        service=ServiceProfile.objects.get(uuid=id)
        
        exec_path=SERVICE_UPLOAD_PATH+"/"+service.exec_name
        
        os.remove(exec_path)
        
        service.delete()
        
        return True
    except ServiceProfile.DoesNotExist:
        return False


def unpack_and_verify_service()->(int,str):
    
    try:
        logging.info("Unpacking the ZTS archive into temporary")
        shutil.unpack_archive(
            filename=SERVICE_TMP_FILE,
            extract_dir=SERVICE_TMP_ARCHIVE,
            format='zip'
        )

        logging.info("Looking for meta.json file")

        # check if meta file exists
        if not os.path.exists(SERVICE_TMP_ARCHIVE+'/meta.json'):
            logging.error("No valid meta.json file")
            return -1,"No valid meta.json file"
        
        logging.info("Loading metadata...")
        
        _json:dict=json.load(open(SERVICE_TMP_ARCHIVE+'/meta.json','r'))

        try:
            # check if meta.json is valid meta file
            meta:ServiceInfo=namedtuple("ServiceInfo",_json.keys())(*_json.values())

            if PublicNodes.get_obj(meta.node) is None:
                clean_temporary()
                return -5,"Couldn't find a required node: "+str(meta.node)
            
            server_version=version_to_number(SERVER_VERSION)
            m_ver=version_to_number(meta.version)

            ver=compare_versions(server_version,m_ver)
            
            if ver<0:
                return -3,"Plugin version is behind server version"
            
            # check if plugin aleardy exits

            try:
                
                serv=ServiceProfile.objects.get(name=meta.name)
                
                return -4,"Service aleardy exits"
                
            except ServiceProfile.DoesNotExist:
                pass
            
                
        except ValueError as e:
            logging.error(str(e))
            return -2,"No valid meta.json file"
        
        return 0,"Ok"
    
    except ValueError as e:
        logging.error("Cannot open archive: "+str(e))
        return -10,"Cannot parse plugin file"


def add_service()->(int,str):
    
    try:
        
        logging.info("Loading metadata...")
        
        if not os.path.exists(SERVICE_TMP_ARCHIVE+'/meta.json'):
            return -1,"No valid meta.json file"
        
        _json:dict=json.load(open(SERVICE_TMP_ARCHIVE+'/meta.json','r'))

        try:
            # check if meta.json is valid meta file
            meta:ServiceInfo=namedtuple("ServiceInfo",_json.keys())(*_json.values())._asdict()
                
        except ValueError as e:
            logging.error(str(e))
            return -1,"No valid meta.json file"
        
        logging.info("Looking for exec file")
        
        #check if folder with django source code exits
        if not os.path.exists(SERVICE_TMP_ARCHIVE+"/"+meta["exec_name"]):
            logging.error("No exec file found")
            clean_temporary()
            return -2,"No exec file found"        

        logging.info("Moving exec file to imported directory")
        
        # in the future let saved service use uuid as a filename
        
        shutil.move(SERVICE_TMP_ARCHIVE+"/"+meta["exec_name"],SERVICE_UPLOAD_PATH)
        
        logging.info("Creating service profile")
        
        service=ServiceProfile()
        
        service.name=meta["name"]
        service.exec_name=meta["exec_name"]
        service.node_name=meta["node"]
        
        service.save()

        logging.info("Cleaning temporary data")

        clean_temporary()

        logging.info("Service has been imported")
        return [0,"Service has been imported"]

    except ValueError as e:
        logging.error("Cannot open archive: "+str(e))
        
        clean_temporary()
        return [-10,"Cannot open archive: "+str(e)]