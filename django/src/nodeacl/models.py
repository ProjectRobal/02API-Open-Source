from django.db import models
from common.models import common
from devices.models import Device
from mqtt.models import Topic
from common.acess_levels import Access

# Create your models here.

class NodeACL(common):
   ''' 
    A class that holds ACL info for each nodes
    '''
   
   access_level=models.IntegerField(verbose_name="access level",choices=Access.choices,default=Access.GET)
   device=models.ForeignKey(Device,on_delete=models.SET_NULL,null=True)
   topic=models.ForeignKey(Topic,on_delete=models.SET_NULL,null=True)
