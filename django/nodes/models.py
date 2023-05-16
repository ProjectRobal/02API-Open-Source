from django.db import models
from common.models import common
from devices.models import Device
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
