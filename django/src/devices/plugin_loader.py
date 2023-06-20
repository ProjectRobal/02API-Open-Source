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

PLUGIN_TMP_FILE="tmp/plugin.tmp"

PLUGIN_TMP_ARCHIVE="tmp/unpacked"

class PluginInfo:
    name:str
    author:str
    installation_date:datetime.datetime
    creation_date:datetime.datetime
    version:str
    app_name:str


def scan_for_plugin()-> list[str]:

    output:list[str]=[]

    for dir in os.listdir('/app/'):
        if os.path.isdir(dir):
            if os.path.exists('/app/'+dir+'/meta.json'):
                output.append(dir)
    
    return output


def parse_plugin(app_name:str)->PluginInfo or None:

    if os.path.exists("/app/"+app_name+"/meta.json"):
    
        _json:dict=json.load(open("/app/"+app_name+"/meta.json","r"))

        return namedtuple("PluginInfo",_json.keys())(*_json.values())


    return None

def clean_temporary():
    os.remove(PLUGIN_TMP_FILE)
    os.remove(PLUGIN_TMP_ARCHIVE)


def add_plugin():
    '''A file with compressed archive'''
    
    try:

        shutil.unpack_archive(
            filename=PLUGIN_TMP_FILE,
            extract_dir=PLUGIN_TMP_ARCHIVE
        )

        # check if meta file exists
        if not os.path.exists(PLUGIN_TMP_ARCHIVE+'meta.json'):
            logging.error("No valid meta.json file")
            clean_temporary()
            return

    except ValueError:
        logging.error("Cannot open archive")
        clean_temporary()

    



