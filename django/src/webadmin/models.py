from django.db import models
from django.contrib.auth.models import User
from django.db import DEFAULT_DB_ALIAS
from domena.settings import MEDIA_ROOT

from common.models import common

import os


# Create your models here.

class ProjectGroup(common):
    name=models.CharField(verbose_name="Name",max_length=255)
    project_name=models.CharField(verbose_name="Nazwa projektu",max_length=255)

    user=models.ManyToManyField(User)

class ProfilePicture(common):
    '''
    A model for storing profile pictures.
    '''
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    path=models.CharField(name="filepath")

    def delete(self, using = DEFAULT_DB_ALIAS, keep_parents: bool = False) -> tuple[int, dict[str, int]]:

        os.remove(os.path.join(MEDIA_ROOT, self.path))
        
        return super().delete(using,keep_parents)