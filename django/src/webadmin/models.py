from django.db import models
from django.db import DEFAULT_DB_ALIAS
from domena.settings import MEDIA_ROOT
from auth02.models import O2User
from common.models import common
import secrets

from uuid import uuid4
import os

from nodes.models import PublicNode

# plugin nodes

class CardNode(PublicNode):
        '''
        A node that represents each cards,
        '''
        _name="cards"
        hash_key=models.BinaryField(name="key",max_length=32,default=secrets.token_bytes(32))
        user_id=models.ForeignKey(O2User, on_delete=models.CASCADE)
        is_in_basement=models.BooleanField(default=False)

        class Meta:
            permissions = [
                ("cards_view", "Can see who is in the basement")
            ]

class BasementStatus(PublicNode):
    _name="piwnica"
    _mono=True
    busy=models.BooleanField()

# Create your models here.

class ProjectGroup(common):
    name=models.CharField(verbose_name="Name",max_length=255)
    project_name=models.CharField(verbose_name="Nazwa projektu",max_length=255)

    user=models.ManyToManyField(O2User)

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
    
