from typing import Any, Dict, Tuple
from django.db import models
from django.db import DEFAULT_DB_ALIAS
from django.core.validators import RegexValidator 
import django.forms as forms
from nodes.models import PublicNodes
from .apps import MqttConfig
from common.models import common
import logging

from common.regexs import topic_regex


# Create your models here.

class Topic(common):

    '''
    A class that holds path for api communications
    
    path - a path to a node aka. (<path>)
    node - a name of a node,topic is referring to
    '''

    path=models.CharField(max_length=255,name="path",unique=True,validators=[RegexValidator(topic_regex,"String is not a valid path, must be path /.../ ")])
    node=models.CharField(max_length=255,name="node")

    def save(self, *args, **kwargs):

        from common.fetch_api import Fetch

        try:
            logging.debug("Unsubscribed to topics: ")

            past_topic=Topic.objects.get(uuid=self.uuid)

            for key in Fetch.requests.keys():
                topic=past_topic.path+"/"+key
                #MqttConfig.client.unsubscribe(topic)
                MqttConfig.client.unsubscribe(topic)
                logging.debug(topic)

        except Topic.DoesNotExist:
            logging.debug("Brand new topic!")

        logging.debug("Subscribed to topics: ")

        if MqttConfig.client is not None:
            for key in Fetch.requests.keys():
                topic=self.path+"/"+key
                #MqttConfig.client.unsubscribe(topic)
                MqttConfig.client.subscribe(topic)
                logging.debug(topic)
                

        super().save(*args, **kwargs)

    def delete(self, using: Any = DEFAULT_DB_ALIAS, keep_parents: bool = False) -> tuple[int, dict[str, int]]:

        from common.fetch_api import Fetch

        logging.debug("Unsubscribed to topics: ")

        if MqttConfig.client is not None:
            for key in Fetch.requests.keys():
                topic=self.path+"/"+key
                MqttConfig.client.unsubscribe(topic)
                logging.debug(topic)

        return super().delete(using, keep_parents)
    

class TopicForm(forms.ModelForm):
    node=forms.ChoiceField(choices=PublicNodes.get_nodes_list)
    class Meta:
        model=Topic
        fields = ["path","node"]

class TopicCatcher(common):

    path=models.CharField(max_length=255,name="path",unique=True,validators=[RegexValidator(topic_regex,"String is not a valid path, must be path /.../ ")])
    node=models.CharField(max_length=255,name="node")

    def save(self, *args, **kwargs):

        logging.debug("Catcher subscribed to topics: ")

        if MqttConfig.client is not None:
            MqttConfig.client.subscribe(self.path)
            logging.debug(self.path)
                

        super().save(*args, **kwargs)

    def delete(self, using: Any = DEFAULT_DB_ALIAS, keep_parents: bool = False) -> tuple[int, dict[str, int]]:

        logging.debug("Unsubscribed to topics: ")

        if MqttConfig.client is not None:
            MqttConfig.client.unsubscribe(self.path)
            logging.debug(self.path)

        return super().delete(using, keep_parents)
    

class TopicBeamer(common):
    '''
        A topic that will be asigned to nodes that will publish data into it.
    '''
    path=models.CharField(max_length=255,name="path",unique=True,validators=[RegexValidator(topic_regex,"String is not a valid path, must be path /.../ ")])
    node=models.CharField(max_length=255,name="node")