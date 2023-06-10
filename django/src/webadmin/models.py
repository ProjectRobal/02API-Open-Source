from django.db import models
from django.contrib.auth.models import User

from common.models import common

# Create your models here.

class ProjectGroup(common):
    name=models.CharField(verbose_name="Name",max_length=255)
    project_name=models.CharField(verbose_name="Nazwa projektu",max_length=255)

    user=models.ManyToManyField(User)