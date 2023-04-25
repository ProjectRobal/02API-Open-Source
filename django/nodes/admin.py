from django.contrib import admin
from .models import PublicNodes,DeviceNode

# Register your models here.

admin.site.register(PublicNodes.SampleNode)

admin.site.register(DeviceNode)