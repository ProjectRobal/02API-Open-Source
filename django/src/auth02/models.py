import logging
import uuid
from django.db import models


from django.contrib.auth.models import AbstractUser
from django.db import models
from common.models import common

from django.apps import AppConfig

# Create your models here.

class O2User(AbstractUser):
    uuid=models.UUIDField(default=uuid.uuid4,
                                primary_key=True,
                               editable=False)
    
def get_user_by_id(id)->O2User|None:
    try:
        
        return O2User.objects.get(uuid=id)
        
    except O2User.DoesNotExist:
        return None


class PluginGroup(common):
    appname=models.CharField(verbose_name="App name",max_length=255)

    user=models.ManyToManyField(O2User,blank=True)

    @staticmethod
    def createPluginGroup(app:AppConfig|str):
        if isinstance(app,AppConfig):
                app=app.name

        n_group=PluginGroup(appname=app)

        n_group.save()

        logging.info("New plugin group created")

        return n_group

    @staticmethod
    def initPluginUserGroup(app:AppConfig):
        try:
            obj=PluginGroup.objects.get(appname=app.name)

            return obj

        except PluginGroup.DoesNotExist:
            
            return PluginGroup.createPluginGroup(app)

    @staticmethod
    def AppPlugin(app:AppConfig|str):
        if isinstance(app,AppConfig):
                app=app.name

        try:
             
            group=PluginGroup.objects.get(appname=app)

            return group
        
        except PluginGroup.DoesNotExist:
             
            return PluginGroup.createPluginGroup(app)