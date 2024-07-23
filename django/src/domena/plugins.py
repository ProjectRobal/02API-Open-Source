'''
A scirpt that stores externals plugins names

Obsolite for now
'''

from django.urls import path
from domena.home import entries
from domena.menu import entries as menu_entries
from domena.menu_types import HomeBlock,MenuBlock

import os
import json


PLUGINS:list[str]=[
"webadmin"
]

def addURL(path_:str,response):
    from domena.urls import urlpatterns
    urlpatterns.append(path(path_,response))
    
def scan_for_plugin()-> list[str]:

    output:list[str]=[]
    
    try:

        for dir in os.listdir('/app/'):
            if os.path.isdir(dir):
                if os.path.exists('/app/'+dir+'/meta.json'):
                    output.append(dir)
    except Exception:
        return []
    
    return output

def get_meta(app_name:str)-> dict:
    if os.path.isdir('/app/'+app_name):
            if os.path.exists('/app/'+app_name+'/meta.json'):
                return json.load(open('/app/'+app_name+'/meta.json',"r"))
    