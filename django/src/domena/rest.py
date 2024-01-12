'''
A file that stores all REST API views.

'''

from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from rest_framework.views import APIView
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework import generics
from rest_framework import permissions

import domena.rest_api_exceptions as exceptions

from knox.views import LoginView as KnoxLoginView
from knox.auth import TokenAuthentication
from django.contrib.auth import authenticate,login
from django.contrib.auth.models import Permission

from auth02.models import O2User

import domena.rest_serializers as rest_serializers

from devices.models import Device
from domena.settings import PLUGINS_LIST





class PluginView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self,request, format=None):
        
        plugin_name=rest_serializers.PluginViewSerializer(request.data).name

        if not plugin_name in PLUGINS_LIST:
            return NotFound("No plugin with name {}".format(plugin_name))

        try:
            meta_data=open("/app/{}/meta.json","r")
        except OSError: 
            return NotFound("Cannot find metadata for plugin {}".format(plugin_name))

        meta=rest_serializers.PluginMetaSerializer(meta_data.read())

        meta_data.close()

        return Response(meta.data)

class PluginList(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self,request, format=None):
        
        return Response(PLUGINS_LIST)

class DeviceView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):

        uuid=rest_serializers.UUIDParser(request.data).uuid

        user=request.user

        if len(uuid)>0:
            try:
                user=Device.objects.get(uuid)
            except Device.DoesNotExist:
                return NotFound("Device not found")
       
        return Response(rest_serializers.DeviceSerializer(user).data)


class DeviceList(generics.ListCreateAPIView):
    queryset=Device.objects.all()
    serializer_class=rest_serializers.DeviceSerializer
    permission_classes=[permissions.DjangoModelPermissions,]



class LoginView(KnoxLoginView):
    serializer_class=rest_serializers.AuthSerializer 
    permission_classes=(AllowAny,)

    def post(self,request,format=None):
        serializer=AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user= serializer.validated_data['user']
        login(request,user)       
        return super().post(request,format=None)

class ExampleView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        content = {
            'user': str(request.user),  # `django.contrib.auth.User` instance.
            'auth': str(request.auth),  # None
        }
        return Response(content)
    
class UserView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):

        uuid=rest_serializers.UUIDParser(request.data).uuid

        user=request.user

        if len(uuid)>0:
            try:
                user=O2User.objects.get(uuid)
            except O2User.DoesNotExist:
                return NotFound("User not found")
       
        return Response(rest_serializers.UserSerializer(user).data)
    
class UserPermissionView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):

        uuid=rest_serializers.UUIDParser(request.data).uuid

        user=request.user

        if len(uuid)>0:
            try:
                user=O2User.objects.get(uuid)
            except O2User.DoesNotExist:
                return NotFound("User not found")

        out=[]

        if user.is_superuser:
            out=Permission.objects.all()
        else:
            out=user.user_permissions.all()

        return Response(rest_serializers.UserPermissionSerializer(out,many=True).data)


class RegisterView(APIView):
    authentication_classes = ()
    permission_classes=(AllowAny,)

    def post(self,request,format=None):
        serializer=rest_serializers.UserRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data

        try:
            
            O2User.objects.get(username=user["username"])

            return exceptions.UserExits()
            
        except O2User.DoesNotExist:
            register_user=O2User(
                username=user["username"],
                password=user["password"],
                first_name=user["first_name"],
                last_name=user["last_name"],
                email=user["email"]
            )

            register_user.save()
        
        return Response('Succesfully registered user with username: {}'.format(register_user.username))