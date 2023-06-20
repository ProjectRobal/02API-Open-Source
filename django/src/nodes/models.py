from django.db import models
from common.models import common
from devices.models import Device
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.models import User
import inspect
from typing import Tuple
from common.acess_levels import Access

# Create your models here.

class NodeEntry(common):
    '''
    A base class for every node

    _name - alternate node name
    '''
    _name=None
    class Meta:
        abstract = True
        app_label= "nodes"


class PublicNode(NodeEntry):
    '''
    A base class for public nodes
    '''
    _name=None
    class Meta:
        abstract = True
        app_label= "nodes"


class LedControllerMarcin(PublicNode):

    _name="marcin"
    led_freq=ArrayField(base_field=models.IntegerField(default=0),name="frequency",size=16)
    led_prec=ArrayField(base_field=models.IntegerField(default=0),name="brightness",size=16)


class SampleNode(PublicNode):
    '''
    A sample node for class entry
    '''
    temperature=models.FloatField(name="temperature")
    humidity=models.FloatField(name="humidity")
    _name="sample"

class PublicNodes:

    def get_nodes_list()->list[Tuple[str,str]]:

        output:list[Tuple[str,str]]=[
        ]

        childs:list[PublicNode]=PublicNode.__subclasses__()

        for child in childs:
            if child._name is None:
                output.append((child.__class__.__name__,child.__class__.__name__))
            else:
                output.append((child.__class__.__name__,child._name))

        if len(childs)==0:
            output.append(("",""))

        return output

    def get_node():

        return PublicNode.__subclasses__()
    
    def get_obj(name:str):
        childs:list[PublicNode]=PublicNode.__subclasses__()

        for child in childs:
            if child._name is None:
                if name == child._name:
                    return child
            elif child.__class__.__name__==name:
                return child
        
        return None
