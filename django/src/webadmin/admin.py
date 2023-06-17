from django.contrib import admin
from .models import ProjectGroup,ProfilePicture,ProfileUser

# Register your models here.

admin.site.register(ProjectGroup)
admin.site.register(ProfileUser)
admin.site.register(ProfilePicture)