from django.db import models
from devices.models import Device
from common.fetch_api import Access

# Create your models here.

class Topics(models.Model):

    '''
    A class that holds path for api communications
    
    path - a path to a node aka. (<path>)
    device - a name of the device topic is pointing to
    node - a name of a node topic is pointing to
    '''

    path=models.CharField(max_length=255,name="path",unique=True,primary_key=True)
    node=models.CharField(max_length=255,name="node",unique=True)
    access=models.IntegerField(choices=Access.choices,default=Access.READ)