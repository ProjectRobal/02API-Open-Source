from django.db import models
from common.models import common
from devices.models import Device

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
    '''
    def __str__(self):
        return self.__name__
    
    

class SampleNode(NodeEntry):
    '''
    A sample node for class entry
    '''
    temperature=models.FloatField(name="temperatura")
    humidity=models.FloatField(name="wilgotność")

