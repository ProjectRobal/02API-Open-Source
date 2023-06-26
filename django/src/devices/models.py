from django.db import models
from common.models import common
import django.utils as utils
from .protocols import Protocols
import secrets

# Create your models here.



class Device(common):
    _status=[
        (0,"AVAILABLE"),
        (1,"BUSY")
    ]
    '''
    A model that will hold all registered devices in a system.

    identificator - a unique identificator for device
    name - a name of the device
    key - a key used for authentication
    last_login_date - last time device was logged in
    status - current device status
    major_version
    minor_version
    patch_version

    A version string: major_version.minor_version.patch_version
    '''
    name= models.CharField(max_length=64)
    last_login_date=models.DateTimeField(blank=True,null=True)
    key=models.CharField(max_length=32,unique=True,default=secrets.token_urlsafe(24))
    status=models.IntegerField(choices=_status,default=_status[0])
    version=models.CharField(max_length=5,default="0.0.0")
    
    class Meta:
            permissions = [
                ("device_view", "Can access device page"),
                ("device_user","Can create other users with device admin"),
                ("device_add","Can add devices"),
                ("device_rm","Can remove devices"),
                ("node_rm","Can remove node"),
                ("topic_rm","Can remove topic"),
                ("plugin_add","Can add plugins"),
                ("plugin_rm","Can remove plugins"),
                ("plugin_view","Can view plugins")
            ]
 

class SupportedProtocols(common):

    '''
    A model that will hold a list of protocols supported by device
    '''
    protocol=models.IntegerField(choices=Protocols.choices)
    device=models.ForeignKey(Device,on_delete=models.SET_NULL,null=True)