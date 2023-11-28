'''
A scirpt that stores externals plugins names

Obsolite for now
'''

from django.urls import path
from domena.home import entries
from domena.menu import entries as menu_entries
from domena.menu_types import HomeBlock,MenuBlock

PLUGINS:list[str]=[
"webadmin"
]

def addURL(path_:str,response):
    from domena.urls import urlpatterns
    urlpatterns.append(path(path_,response))


    