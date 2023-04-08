from django.db import models
from common.models import common

# Create your models here.

class Device(common):
        '''
    name - name of the device
    register_date - a date when device was registered
    last_login_date - a date when device was last logged in
        '''
        name= models.CharField(max_length=64,unique=True)
        register_date= models.DateTimeField(blank=True,null=True)
        last_login_date=models.DateTimeField(blank=True,null=True)
        status=models.IntegerChoices('DeviceStatus',"DISCONNECTED CONNECTED BUSY BOOTTING")

        def __str__(self):
            return self.name