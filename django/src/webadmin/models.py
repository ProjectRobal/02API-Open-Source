from collections.abc import Iterable
from typing import Iterable, Optional
from django.db import models
from django.core.files import File
from django.db import DEFAULT_DB_ALIAS
from domena.settings import MEDIA_ROOT
from auth02.models import O2User
from common.models import common
import secrets
from io import BytesIO
import datetime

from PIL import Image

from uuid import uuid4
import os

from nodes.models import PublicNode,MonoNode

import logging

class CardVisitRecord(common):
    '''
        A model that holds record in who entered/left basement on specific date
    '''

    user=models.ForeignKey(O2User,on_delete=models.SET_NULL,null=True)
    data=models.DateTimeField(default=datetime.datetime.now())
    has_entered=models.BooleanField()



# plugin nodes

PROFILE_WIDTH=800
PROFILE_HEIGHT=600


def gen_key()->bytes:

    key=secrets.token_urlsafe(24)

    while CardNode.objects.filter(key=key).count()>0:
        key=secrets.token_urlsafe(24)
    
    return key



class CardNode(PublicNode):
        '''
        A node that represents each cards,
        '''
        _name="cards"
        hash_key=models.CharField(name="key",max_length=32,default=gen_key,unique=True)
        user=models.ForeignKey(O2User, on_delete=models.CASCADE)
        is_in_basement=models.BooleanField(default=False)

        class Meta:
            permissions = [
                ("cards_view", "Can see who is in the basement")
            ]

        def save(self,*args, **kwargs) -> None:

            try:

                past=CardNode.objects.get(uuid=self.uuid)
                
                visit=CardVisitRecord()
                visit.user=self.user
                if not past.is_in_basement and self.is_in_basement:
                    visit.has_entered=True
                    visit.save()
                elif past.is_in_basement and not self.is_in_basement:
                    visit.has_entered=False
                    visit.save()
            except CardNode.DoesNotExist:
                pass

            return super(CardNode,self).save(*args,**kwargs)

class BasementStatus(MonoNode,PublicNode):
    _name="piwnica"
    busy=models.BooleanField()

# Create your models here.

class ProjectGroup(common):
    name=models.CharField(verbose_name="Name",max_length=255)
    project_name=models.CharField(verbose_name="Nazwa projektu",max_length=255)

    user=models.ManyToManyField(O2User,blank=True)

def user_directory_path(instance, filename):
    
    name=uuid4()

    while os.path.exists('{0}/{1}'.format(MEDIA_ROOT,str(name))):
        name=uuid4()
    
    return 'profiles/{0}'.format(str(name))


class ProfilePicture(common):
    '''
    A model for storing profile pictures.
    '''
    user=models.OneToOneField(O2User,on_delete=models.CASCADE)
    image=models.ImageField(upload_to=user_directory_path)

    def delete(self, using = DEFAULT_DB_ALIAS, keep_parents: bool = False) -> tuple[int, dict[str, int]]:

        #os.remove(os.path.join(MEDIA_ROOT, self.path))
        
        return super().delete(using,keep_parents)
    
    def save(self,*args, **kwargs):
        
        im:Image=Image.open(self.image)

        im.convert('RGB')

        im.thumbnail((PROFILE_WIDTH,PROFILE_HEIGHT))

        thumb_io = BytesIO()

        im.save(thumb_io,'webp')

        self.image=File(thumb_io, name=self.image.name)

        return super(ProfilePicture, self).save(*args, **kwargs)