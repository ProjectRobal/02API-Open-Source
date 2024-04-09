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
from devices.views import devsPage,twingoPage,device_page,node_list,home_page,rat,plugin_add,ploader,plugin_show,plugin_rm,device_add,devloader,device_rm,device_purge,api
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static

import domena.rest as rest
import domena.settings as settings
from knox import views as knox_views

urlpatterns = [

    path('',home_page),
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

    #handle path in format api/<path> like api/samples/
    path('accounts/', include('allauth.urls')),
    path('api/<path:path>',api),
    #path('api/<str:path>/<str:cmd>',api),
    path('devs/',devsPage),
    path('django-admin/', admin.site.urls),
    path('hello/<str:name>',home_page),
    path('twingo/',twingoPage),
    path('device/<str:name>',device_page),
    path('nodes/<str:name>',node_list),
    path('plugin_add/',plugin_add),
    path('device_add',device_add),
    path('pshow/<str:name>',plugin_show),
    path('prm/',plugin_rm),
    path('devrm/',device_rm),
    path('devpr/',device_purge),
    path('ploader/',ploader),
    path('devloader/',devloader),
    path('ave_prezes',rat)
]

if os.environ.get("DJANGO_MODE") == 'DEBUG':
    urlpatterns.append(path("__reload__/", include("django_browser_reload.urls")))
    
urlpatterns+=staticfiles_urlpatterns()
