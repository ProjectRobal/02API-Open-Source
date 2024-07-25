from django.contrib import admin
from .models import PublicNodes

from nodes.imported import *


# Register your models here.



for node in PublicNodes.get_node():

    admin.site.register(node)