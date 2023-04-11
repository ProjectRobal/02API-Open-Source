from django.db import models
from devices.models import Device

# Create your models here.

class Topics(models.Model):
    '''
    A class that holds path for api communications
    
    path - a path to a node aka. (<path>)
    device - a name of the device topic is pointing to
    node - a name of a node topic is pointing to
    '''

    path=models.CharField(max_length=512,name="path",unique=True,primary_key=True)
    device=models.ForeignKey(Device,on_delete=models.PROTECT)
    node=models.CharField(max_length=255,name="node",unique=True)