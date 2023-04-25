from django.db import models
from common.models import common
from devices.models import Device
from enum import Enum
import inspect
from typing import Tuple
import logging
import secrets
import base64
import datetime

# Create your models here.


class NodeACL(common):
    '''
    A class that holds ACL info for each nodes
    '''
    read=models.BooleanField(name="read")
    write=models.BooleanField(name="write")
    modify=models.BooleanField(name="modify")

class NodeEntry(common):
    '''
    A base class for every node

    _name - alternate node name
    '''
    _name=None


class DeviceNode(NodeEntry):
    _status=[
        (0,"DISCONNECTED"),
        (1,"CONNECTED"),
        (2,"BUSY")
    ]
    '''
    A model that will hold all registered devices in a system.

    identificator - a unique identificator for device
    name - a name of the device
    key - a key used for authentication
    last_login_date - last time device was logged in
    register_date - when device was registered
    password - a password for login in
    status - current device status
    '''
    _name="device"
    name= models.CharField(max_length=64)
    register_date= models.DateTimeField(blank=True,null=True,default=datetime.datetime.today())
    last_login_date=models.DateTimeField(blank=True,null=True)
    identificator=models.CharField(max_length=32,unique=True)
    key=models.CharField(max_length=256,editable=False)
    password=models.CharField(max_length=32,default=secrets.token_urlsafe(24))
    status=models.IntegerField(choices=_status,default=_status[0])



class PublicNodes:    
    
    class SampleNode(NodeEntry):
        '''
        A sample node for class entry
        '''
        temperature=models.FloatField(name="temperature")
        humidity=models.FloatField(name="humidity")
        _name="sample"

    def get_nodes_list()->list[Tuple[str,str]]:

        output:list[Tuple[str,str]]=[
            ("","")
        ]

        for o in inspect.getmembers(PublicNodes,lambda a:inspect.isclass(a)):
            if issubclass(o[1],NodeEntry):
                #logging.debug(o[1]._name)
                if o[1]._name is None:
                    output.append((o[0],o[0]))
                else:
                    
                    output.append((o[0],o[1]._name))

        return output
    
    def get_obj(name:str):
        if hasattr(PublicNodes,name):
            return getattr(PublicNodes,name)
        else:
            return None
