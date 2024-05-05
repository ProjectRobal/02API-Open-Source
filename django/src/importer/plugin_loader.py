'''
A script that loads plugins

Every plugins has it's own meta file called meta.json

example meta.json:

{
    "name":"Cards web manager",
    "author":"02",
    "installation_date":"2023-06-20T11:56:00Z",
    "creation_date":"2012-04-23T00:00:00Z",
    "version":"0.5.0",
    "app_name":"webadmin"
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



PLUGIN_TMP_FILE="tmp/plugin.tmp"

PLUGIN_TMP_ARCHIVE="tmp/unpacked"

# zero two plugin extension
PLUGIN_ARCHIVE_EXTENSION="ztp"

class PluginInfo:
    name:str
    author:str
    installation_date:datetime.datetime
    creation_date:datetime.datetime
    version:str
    app_name:str



def parse_plugin(app_name:str)->PluginInfo or None:

    if os.path.exists("/app/"+app_name+"/meta.json"):
    
        _json:dict=json.load(open("/app/"+app_name+"/meta.json","r"))

        return namedtuple("PluginInfo",_json.keys())(*_json.values())


    return None

def clean_temporary():
    shutil.rmtree('tmp', ignore_errors=True)

def remove_plugin(name:str)->bool:
    if not name in PLUGINS_LIST:
        return False
    
    if os.path.exists("/app/"+name):
        shutil.rmtree("/app/"+name,ignore_errors=True)
        return True

    return False


def unpack_and_verify_plugin()->(int,str):
    
    try:
        logging.info("Unpacking the ZTP archive into temporary")
        shutil.unpack_archive(
            filename=PLUGIN_TMP_FILE,
            extract_dir=PLUGIN_TMP_ARCHIVE,
            format='zip'
        )

        logging.info("Looking for meta.json file")

        # check if meta file exists
        if not os.path.exists(PLUGIN_TMP_ARCHIVE+'/meta.json'):
            logging.error("No valid meta.json file")
            return -1,"No valid meta.json file"
        
        logging.info("Loading metadata...")
        
        _json:dict=json.load(open(PLUGIN_TMP_ARCHIVE+'/meta.json','r'))

        try:
            # check if meta.json is valid meta file
            meta:PluginInfo=namedtuple("PluginInfo",_json.keys())(*_json.values())
            
            server_version=version_to_number(SERVER_VERSION)
            m_ver=version_to_number(meta.version)

            ver=compare_versions(server_version,m_ver)
            
            if ver<0:
                return -3,"Plugin version is behind server version"
            
            # check if plugin aleardy exits
            
            curr_meta:PluginInfo=parse_plugin(meta.app_name)
            
            if curr_meta is not None:
                cm_ver=version_to_number(curr_meta.version)
                ver=compare_versions(m_ver,cm_ver)
                
                if ver<0:
                    return -4,"There is aleardy newest version of that plugin"

                if ver>0:
                    return -4,"Plugin version mismatch with server version"
                
        except ValueError as e:
            logging.error(str(e))
            return -2,"No valid meta.json file"
        
        return 0,"Ok"
    
    except ValueError as e:
        logging.error("Cannot open archive: "+str(e))
        return -10,"Cannot parse plugin file"


def add_plugin()->(int,str):
    
    try:
        
        logging.info("Loading metadata...")
        
        if not os.path.exists(PLUGIN_TMP_ARCHIVE+'/meta.json'):
            return -1,"No valid meta.json file"
        
        _json:dict=json.load(open(PLUGIN_TMP_ARCHIVE+'/meta.json','r'))

        try:
            # check if meta.json is valid meta file
            meta:PluginInfo=namedtuple("PluginInfo",_json.keys())(*_json.values())._asdict()
                
        except ValueError as e:
            logging.error(str(e))
            return -1,"No valid meta.json file"
        
        logging.info("Looking for source code")
        
        #check if folder with django source code exits
        if not os.path.exists(PLUGIN_TMP_ARCHIVE+"/src"):
            logging.error("No source code has been found")
            clean_temporary()
            return -2,"No source code has been found"
        
        app_dir:str="/app/"+meta["app_name"]
        
            
        meta["installation_date"]=datetime.datetime.today()
        
        if os.path.exists(app_dir):
            logging.info("Found exiting plugin "+str(meta["app_name"])+" instance")
            logging.info("Moving to temporary")
            
            if not os.path.exists(PLUGIN_TMP_ARCHIVE+"/copy"):
                os.mkdir(PLUGIN_TMP_ARCHIVE+"/copy")
            
            if os.path.exists(PLUGIN_TMP_ARCHIVE+"/copy/"+meta["app_name"]):
                shutil.rmtree(PLUGIN_TMP_ARCHIVE+"/copy/"+meta["app_name"],ignore_errors=True)
                
            shutil.move(app_dir,PLUGIN_TMP_ARCHIVE+"/copy",)
        
        logging.info("Creating a folder for: "+meta["app_name"])
        
        os.mkdir(app_dir)

        logging.info("Creating meta.json file to a new directory")
        
        with open(app_dir+"/meta.json","wb+") as meta_file:
            meta_file.write(json.dumps(meta,cls=DjangoJSONEncoder).encode())

        # move meta.json file
        #shutil.move(PLUGIN_TMP_ARCHIVE+"/meta.json",app_dir+"/meta.json")

        logging.info("Moving source into a new directory")
        
        allfiles = os.listdir(PLUGIN_TMP_ARCHIVE+"/src/")

        # move src to app source
        for file in allfiles:
            shutil.move(PLUGIN_TMP_ARCHIVE+"/src/"+file,app_dir)

        logging.info("Cleaning temporary data")

        clean_temporary()

        logging.info("App has been imported")
        global PLUGINS_LIST
        PLUGINS_LIST.append(meta["app_name"])
        return [0,"App has been imported"]

    except ValueError as e:
        logging.error("Cannot open archive: "+str(e))
        
        # in case of failure bring back a copy of existing plugin
        if os.path.exists(PLUGIN_TMP_ARCHIVE+"/copy"):
                if app_dir is not None:
                    shutil.rmtree(app_dir)
                    
                    shutil.move(PLUGIN_TMP_ARCHIVE+"/copy",app_dir)
        
        clean_temporary()
        return [-10,"Cannot open archive: "+str(e)]