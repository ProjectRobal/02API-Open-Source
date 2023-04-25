from django.db import models
from common.models import common
from devices.models import Device
from enum import Enum
import inspect
from typing import Tuple
import logging

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

class PublicNodes:    
    
    class SampleNode(NodeEntry):
        '''
        A sample node for class entry
        '''
        temperature=models.FloatField(name="temperature")
        humidity=models.FloatField(name="humidity")

    def get_nodes_list()->list[Tuple[str,str]]:

        output:list[Tuple[str,str]]=[
            ("","")
        ]

        for o in inspect.getmembers(PublicNodes,lambda a:inspect.isclass(a)):
            if issubclass(o[1],NodeEntry):
                logging.debug(o[0])
                if o[1]._name is None:
                    output.append((o[0],o[0]))
                else:
                    output.append((o[1]._name,o[0]))

        return output
    
    def get_obj(name:str):
        if hasattr(name):
            return getattr(PublicNodes,name)
        else:
            return None
