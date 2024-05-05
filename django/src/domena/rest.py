'''
A file that stores all REST API views.

'''

from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.response import Response
from rest_framework.exceptions import NotFound,ParseError
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
from rest_framework.parsers import FileUploadParser

from common.fetch_api import Fetch

from devices.models import Device
from domena.settings import PLUGINS_LIST

from mqtt.models import Topic,TopicBeamer,TopicCatcher
from nodes.models import PublicNodes,PublicNode
from nodeacl.models import NodeACL

import importer.device_loader as device_loader
import importer.plugin_loader as plugin_loader

import os
import json

import logging

class UploadPluginPackage(APIView):
    authentication_classes = (TokenAuthentication,SessionAuthentication)
    permission_classes = (IsAuthenticated,)

    parser_classes = [FileUploadParser]

    def post(self,request, format=None):
        file_obj = request.FILES['file']

        print(file_obj)
        
        if not os.path.exists("tmp"):
            os.mkdir("tmp")

        with open(plugin_loader.PLUGIN_TMP_FILE,"wb+") as pfile:
            for chunk in file_obj.file.chunks():
                pfile.write(chunk)
        
        file_obj.close()
        
        error=plugin_loader.unpack_and_verify_plugin() 
        
        return Response({'code':error[0],'msg':error[1]})

class RemoveDevice(APIView):
    authentication_classes = (TokenAuthentication,SessionAuthentication)
    permission_classes = (IsAuthenticated,)
    
    def post(self,request,format=None):
        prompt=rest_serializers.DeviceRemoveSerializer(data=request.data)
        
        if not prompt.is_valid():
            return Response({'code':-20,'msg':"No valid request!"})
        
        '''Device removal: 

            1.Get device by uuid
            2.Get all NodeACLs associated with device
            3.Get NodeReference of each node from NodeACLs and decrease it's counter
            4.If counter is 0 remove Node completly with all related Topics
            
        '''
        
        prompt=prompt.validated_data
        
        if device_loader.purge_device(prompt["uuid"]):
            return Response({'code':0,'msg':"Device removed!"})
        else:
            return Response({'code':-1,'msg':"Couldn't remove device"})

class AcceptDeviceInstallation(APIView):
    authentication_classes = (TokenAuthentication,SessionAuthentication)
    permission_classes = (IsAuthenticated,)
    
    def post(self,request,format=None):
        
        prompt=rest_serializers.DeviceInstallationPromptSerializer(data=request.data)
        
        if not prompt.is_valid():
            return Response({'code':-20,'msg':"No valid request!"})
        
        prompt=prompt.validated_data
        
        if prompt['go']:
            error=device_loader.gen_device()
            
            if error[0]>=0:
                dev:Device=error[2]
                # generate nodes, topics, acl and etc
                
                topics,acls = device_loader.add_topics()
                
                ret = device_loader.generate_nodes()
                
                if ret[0] >= 0:
                                        
                    _dev=Device.objects.filter(name=dev.name)
                    
                    if _dev.count()!=0:
                        dev=_dev[0]
                    
                    dev.save()
                    
                    logging.info("Adding topics for device: "+dev.name)
                    
                    for topic in topics:
                        
                        top=Topic.objects.filter(path=topic.path)
                        
                        if top.count()==0:
                            topic.save()
                    
                    
                    logging.info("Adding NodeACLs for device: "+dev.name)
                    
                    for acl in acls:
                        
                        _acl=NodeACL.objects.filter(device=acl.device,topic=acl.topic)
                        
                        if _acl.count()==0:
                            acl.device=dev
                            acl.save()
                    
                    logging.info("Saving device!")
                    
                    error=(0,"Device added!")
                else:
                    error=(-2,"Cannot add device!")
        else:
            error=(1,"OK - Temporary data clean")
        
        device_loader.clean_temporary()
        
        return Response({'code':error[0],'msg':error[1]})

class CheckIfDeviceVersionIsProper(APIView):
    authentication_classes = (TokenAuthentication,SessionAuthentication)
    permission_classes = (IsAuthenticated,)
    
    def get(self,request,format=None):
        
        ret=device_loader.check_device_ver()
        
        return Response({'code':ret[0],'msg':ret[1]})

class UploadDevicePackage(APIView):
    authentication_classes = (TokenAuthentication,SessionAuthentication)
    permission_classes = (IsAuthenticated,)

    parser_classes = [FileUploadParser]

    def post(self,request, format=None):
        file_obj = request.FILES['file']

        print(file_obj)
                
        tmp=open(device_loader.DEVICE_TMP_FILE,"wb")
        
        tmp.write(file_obj.file.read())
        
        tmp.close()
        
        file_obj.close()
        
        error=device_loader.unpack_and_verify_archive()   
        
        return Response({'code':error[0],'msg':error[1]})



class TopicList(APIView):
    authentication_classes = (TokenAuthentication,SessionAuthentication)
    permission_classes = (IsAuthenticated,)

    def get(self,request, format=None):

        topics=rest_serializers.TopicSerializer(Topic.objects.all(),many=True).data
        beamer=rest_serializers.TopicSerializer(TopicBeamer.objects.all(),many=True).data
        catcher=rest_serializers.TopicSerializer(TopicCatcher.objects.all(),many=True).data

        for topic in topics:
            topic["type"]="topic"

        for topic in beamer:
            topic["type"]="beamer"
        
        for topic in catcher:
            topic["type"]="catcher"

        all_topics=topics+beamer+catcher

        return Response(all_topics)
    


def find_node(path:str)->PublicNode:
        try:
            node_topic=Topic.objects.get(path=path).node
        except Topic.DoesNotExist:
            try:
                node_topic=TopicBeamer.objects.get(path=path).node
            except TopicBeamer.DoesNotExist:
                try:
                    node_topic=TopicCatcher.objects.get(path=path).node
                except TopicCatcher.DoesNotExist:
                    return None
        
        return PublicNodes.get_obj(node_topic)

    
class NodeInfo(APIView):
    authentication_classes = (TokenAuthentication,SessionAuthentication)
    permission_classes = (IsAuthenticated,)

    def format_output(self,node:PublicNode):
        output={}
            
        for field in node._meta.get_fields():
            output[field.name]=str(field.help_text)

        return output

    def get(self,request,format=None):
        data_input=rest_serializers.FetchNodeInfoSerializer(request.data)

        if data_input.topic is not None:
            node=find_node(data_input.topic)

            if node is None:
                raise NotFound("No node found with specified topic")
            
            return Response(str(self.format_output(node)))
        
        if data_input.node_name is not None:
            node=PublicNodes.get_obj(data_input.node_name)

            if node is None:
                raise NotFound("No node found with specified name") 

            return Response(str(self.format_output(node)))           
        
        return ParseError("No valid topic or node provided")
    
class NodeView(APIView):
    authentication_classes = (TokenAuthentication,SessionAuthentication)
    permission_classes = (IsAuthenticated,)


    def post(self,request, format=None):
        data_input=rest_serializers.FetchRequestSerializer(request.data)

        path:str=data_input.topic
        data:dict=data_input.data

        node_obj=find_node(path)

        if node_obj is None:
            raise NotFound("No node found for specific path!")

        result=Fetch(None,node_obj,path).post(data)

        return Response(str(result))


    def get(self,request,fromat=None):
        data_input=rest_serializers.FetchRequestSerializer(request.data)

        path:str=data_input.topic
        data:dict=data_input.data

        node_obj=find_node(path)

        if node_obj is None:
            raise NotFound("No node found for specific path!")

        result=Fetch(None,node_obj,path).get(data)

        return Response(str(result))

    def put(self,request,format=None):
        data_input=rest_serializers.FetchRequestSerializer(request.data)

        path:str=data_input.topic
        data:dict=data_input.data

        node_obj=find_node(path)

        if node_obj is None:
            raise NotFound("No node found for specific path!")

        result=Fetch(None,node_obj,path).mod(data)

        return Response(str(result))
    
    def delete(self,request,format=None):
        data_input=rest_serializers.FetchRequestSerializer(request.data)

        path:str=data_input.topic
        data:dict=data_input.data

        node_obj=find_node(path)

        if node_obj is None:
            raise NotFound("No node found for specific path!")

        result=Fetch(None,node_obj,path).pop(data)

        return Response(str(result))
        


class PluginView(APIView):
    authentication_classes = (TokenAuthentication,SessionAuthentication)
    permission_classes = (IsAuthenticated,)

    def get(self,request, format=None):
        
        plugin_name=rest_serializers.PluginViewSerializer(request.data).name

        if not plugin_name in PLUGINS_LIST:
            raise NotFound("No plugin with name {}".format(plugin_name))

        try:
            meta_data=open("/app/{}/meta.json","r")
        except OSError: 
            raise NotFound("Cannot find metadata for plugin {}".format(plugin_name))

        meta=rest_serializers.PluginMetaSerializer(meta_data.read())

        meta_data.close()

        return Response(meta.data)

class PluginList(APIView):
    authentication_classes = (TokenAuthentication,SessionAuthentication)
    permission_classes = (IsAuthenticated,)

    def get(self,request, format=None):
        
        return Response(PLUGINS_LIST)

class DeviceView(APIView):
    authentication_classes = (TokenAuthentication,SessionAuthentication)
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):

        uuid=rest_serializers.UUIDParser(request.data).uuid

        user=request.user

        if len(uuid)>0:
            try:
                user=Device.objects.get(uuid)
            except Device.DoesNotExist:
                raise NotFound("Device not found")
       
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
    authentication_classes = (TokenAuthentication,SessionAuthentication)
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        content = {
            'user': str(request.user),  # `django.contrib.auth.User` instance.
            'auth': str(request.auth),  # None
        }
        return Response(content)
    
    
class UserView(APIView):
    authentication_classes = (TokenAuthentication,SessionAuthentication)
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):

        uuid=rest_serializers.UUIDParser(data=request.data)
        uuid.is_valid(raise_exception=True)
        uuid=uuid.validated_data['uuid']
        user=request.user

        if len(uuid)>0:
            try:
                user=O2User.objects.get(uuid=uuid)
            except O2User.DoesNotExist:
                raise NotFound("User not found")
       
        return Response(rest_serializers.UserSerializer(user).data)
    
class UserPermissionView(APIView):
    authentication_classes = (TokenAuthentication,SessionAuthentication)
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):

        uuid=rest_serializers.UUIDParser(data=request.data)
        uuid.is_valid(raise_exception=True)
        uuid=uuid.validated_data['uuid']

        user=request.user

        if len(uuid)>0:
            try:
                user=O2User.objects.get(uuid=uuid)
            except O2User.DoesNotExist:
                raise NotFound("User not found")

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