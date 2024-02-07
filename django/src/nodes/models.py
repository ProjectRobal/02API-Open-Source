import logging

from django.db import models
from common.models import common
from django.contrib.postgres.fields import ArrayField
from typing import Tuple
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.signals import post_save

from datetime import datetime
import json

# Create your models here.

class NodeEntry(common):
    '''
    A base class for every node

    _name - alternate node name
    '''
    _name=None
    class Meta:
        abstract = True
        app_label= "nodes"
        permissions = [
            ("node_view", "Can view nodes data")
        ]

    @classmethod
    def get_name(cls)->str:
        if cls._name is not None:
            return cls._name
        
        return cls.__name__
    

class PublicNode(NodeEntry):
    '''
    A base class for public nodes
    '''
    _name=None
    class Meta:
        abstract = True
        app_label= "nodes"

class NullNode(NodeEntry):
    '''
    A table that will save no data to database
    It represents the same function as /dev/null in linux 
    '''
    class Meta:
        abstract = True
        managed = False
        app_label= "nodes"
    
    def save(self, *args, **kwargs):
        post_save.send(type(self),instance=self,created=True)

class MonoNode(NodeEntry):
    '''A table will singular entry
    if you try to add another record, the previous one will be overwritten instead'''
    class Meta:
        abstract = True
        app_label= "nodes"
    
    def save(self, *args, **kwargs):

        cls=type(self)

        amount=cls.objects.count()

        if amount>0:

            fields:dict={}
            
            obj=cls.objects.get()

            to_inh=self._meta.get_fields(include_parents=False)
            
            for field in to_inh:
                if field != "uuid":
                    fields[field.name]=field.value_from_object(self)
                    
            fields["created_date"]=obj.created_date
            fields["modified_date"]=datetime.now()

            cls.objects.filter(uuid=obj.uuid).update(**fields)

            return

        super().save(*args, **kwargs)


class BeamerNode(NodeEntry):
    '''
        A node that will post message on mqtt topic,
        when you post something on that node it will send message on specific topic
    '''
    class Meta:
        abstract = True
        app_label= "nodes"

    # def save(self,*args, **kwargs):

    #     from mqtt.models import TopicBeamer
    #     from mqtt.apps import MqttConfig

    #     logging.debug("Node name: "+type(self).__name__)

    #     topics=TopicBeamer.objects.filter(node=type(self).__name__)

    #     if topics.exists():
    #         fields:dict={}

    #         for field in self._meta.get_fields(include_parents=False):
    #             fields[field.name]=field.value_from_object(self)

    #         if "uuid" in fields.keys():
    #             del fields["uuid"]

    #         data:str=json.dumps(fields, cls=DjangoJSONEncoder)

    #         logging.debug("Data to publish: "+data)

    #     for topic in topics:

    #         if MqttConfig.client is not None:
    #             MqttConfig.client.publish(topic.path,data)

    #         logging.debug("Publish data on topic: "+topic.path)

    #     return super().save(*args,**kwargs)

class LedControllerMarcin(BeamerNode,MonoNode,PublicNode):

    _name="marcin"
    led_freq=ArrayField(base_field=models.IntegerField(default=0),name="frequency",size=16)
    led_prec=ArrayField(base_field=models.IntegerField(default=0),name="brightness",size=16)


class SampleNode(BeamerNode,PublicNode):
    '''
    A sample node for class entry
    '''
    temperature=models.FloatField(name="temperature")
    humidity=models.FloatField(name="humidity")
    _name="sample"

class PublicNodes:

    def get_nodes_list()->list[Tuple[str,str]]:

        output:list[Tuple[str,str]]=[]

        childs:list[PublicNode]=PublicNode.__subclasses__()

        logging.debug(str(childs))

        for child in childs:
            if child._name is None:
                output.append((child.__name__,child.__name__))
            else:
                output.append((child.__name__,child._name))

        return output

    def get_node():

        return PublicNode.__subclasses__()
    
    def get_obj(name:str)->PublicNode|None:
        childs:list[PublicNode]=PublicNode.__subclasses__()

        for child in childs:
            if child._name is None:
                if name == child._name:
                    return child
            elif child.__name__ == name:
                return child
        
        return None