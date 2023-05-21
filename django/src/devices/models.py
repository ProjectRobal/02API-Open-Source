from django.db import models
from common.models import common
import datetime
import django.utils as utils

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
    register_date - when device was registered
    status - current device status
    '''
    name= models.CharField(max_length=64)
    register_date= models.DateTimeField(blank=True,null=True,default=utils.timezone.now())
    last_login_date=models.DateTimeField(blank=True,null=True)
    key=models.CharField(max_length=32,unique=True)
    status=models.IntegerField(choices=_status,default=_status[0])
    