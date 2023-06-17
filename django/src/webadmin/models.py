from django.db import models
from django.contrib.auth.models import User
from django.db import DEFAULT_DB_ALIAS
from domena.settings import MEDIA_ROOT
from django.contrib.auth.models import User
from common.models import common

from uuid import uuid4
import os


# Create your models here.

class ProjectGroup(common):
    name=models.CharField(verbose_name="Name",max_length=255)
    project_name=models.CharField(verbose_name="Nazwa projektu",max_length=255)

    user=models.ManyToManyField(User)

def user_directory_path(instance, filename):
    
    name=uuid4()

    while os.path.exists('{0}/{1}'.format(MEDIA_ROOT,str(name))):
        name=uuid4()
    
    return 'profiles/{0}'.format(str(name))

class ProfileUser(common):
    user=models.OneToOneField(User, on_delete=models.CASCADE)
    login=models.CharField(max_length=100)

class ProfilePicture(common):
    '''
    A model for storing profile pictures.
    '''
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    image=models.ImageField(upload_to=user_directory_path)

    def delete(self, using = DEFAULT_DB_ALIAS, keep_parents: bool = False) -> tuple[int, dict[str, int]]:

        #os.remove(os.path.join(MEDIA_ROOT, self.path))
        
        return super().delete(using,keep_parents)