"""domena URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import os
from django.contrib import admin
from django.urls import path,re_path,include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static

import devices.views as device

import domena.rest as rest
import domena.settings as settings
from knox import views as knox_views

urlpatterns = [

    path('',device.home_page),
    path('rest-test',rest.ExampleView.as_view()),
    path('ext/auth/login', rest.LoginView.as_view()),
    path('ext/auth/logout', knox_views.LogoutView.as_view()),
    path('ext/auth/logoutall',  knox_views.LogoutAllView.as_view()),
    path('ext/auth/register',  rest.RegisterView.as_view()),
    path('ext/auth/user',rest.UserView.as_view()),
    path('ext/auth/perms',rest.UserPermissionView.as_view()),
    path('ext/devls',rest.DeviceList.as_view()),
    path('ext/dev',rest.DeviceView.as_view()),
    path('ext/pluginls',rest.PluginList.as_view()),
    path('ext/pluginmeta',rest.PluginView.as_view()),
    path('ext/node',rest.NodeView.as_view()),
    path('ext/nodeinfo',rest.NodeInfo.as_view()),
    path('ext/topicls',rest.TopicList.as_view()),
    
    path('ext/dev/upload',rest.UploadDevicePackage.as_view()),
    path('ext/dev/add',rest.AcceptDeviceInstallation.as_view()),
    path('ext/dev/vcheck',rest.CheckIfDeviceVersionIsProper.as_view()),
    path('ext/dev/devrm',rest.RemoveDevice.as_view()),
    
    path('ext/plug/upload',rest.UploadPluginPackage.as_view()),
    path('ext/plug/add',rest.AcceptPluginInstallation.as_view()),
    path('ext/plug/rm',rest.RemovePlugin.as_view()),
    
    path('ext/serv/upload',rest.UploadServicePackage.as_view()),
    path('ext/serv/add',rest.AcceptServiceInstallation.as_view()),
    path('ext/serv/rm',rest.RemoveService.as_view()),

    #handle path in format api/<path> like api/samples/
    path('accounts/', include('allauth.urls')),
    path('api/<path:path>',device.api),
    #path('api/<str:path>/<str:cmd>',api),
    path('devs/',device.devsPage),
    path('django-admin/', admin.site.urls),
    path('hello/<str:name>',device.home_page),
    path('twingo/',device.twingoPage),
    path('device_list',device.device_list),
    path('device/<str:name>',device.device_page),
    path('nodes/<str:name>',device.node_list),
    path('pshow/<str:name>',device.plugin_show),
    path('prm/',device.plugin_rm),
    path('plugins_list',device.plugin_list),
    path('node_list',device.list_node),
    path('serv_list',device.serv_list),
    path('devrm/',device.device_rm),
    path('devpr/',device.device_purge),
    path('ploader/',device.ploader),
    path('ave_prezes',device.rat)
]

if os.environ.get("DJANGO_MODE") == 'DEBUG':
    urlpatterns.append(path("__reload__/", include("django_browser_reload.urls")))
    
urlpatterns+=staticfiles_urlpatterns()
