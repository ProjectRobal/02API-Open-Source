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