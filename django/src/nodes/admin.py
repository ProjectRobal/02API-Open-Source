from django.contrib import admin
from .models import PublicNodes

# Register your models here.

#admin.site.register(PublicNodes.SampleNode)

#admin.site.register(PublicNodes.CardNode)


for node in PublicNodes.get_nodes_list():

    obj=PublicNodes.get_obj(node[0])

    if obj is not None:
        admin.site.register(obj)