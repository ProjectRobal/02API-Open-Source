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
from django.contrib import admin
from django.urls import path
from devices.views import devsPage,twingoPage,device_page,node_list,home_page
from webadmin.views import login_form,auth,unauth,perm_fail,reg_form,reg

urlpatterns = [
    path('devs/',devsPage),
    path('login/',login_form),
    path('auth/',auth),
    path('unauth/',unauth),
    path('permf/',perm_fail),
    path('register/',reg_form),
    path('reg/',reg),
    path('django-admin/', admin.site.urls),

    path('',home_page),
    path('hello/<str:name>',home_page),
    path('twingo/',twingoPage),
    path('device/<str:name>',device_page),
    path('nodes/<str:name>',node_list)
]
