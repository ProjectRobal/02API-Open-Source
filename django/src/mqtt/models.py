import re
from typing import Any, Dict, Tuple
from django.db import models
from django.db import DEFAULT_DB_ALIAS
from django.core.validators import RegexValidator 
from nodes.models import PublicNodes
from .apps import MqttConfig
from common.models import common
import logging

# It ensures that topic path has a form of /.../
regex_path=re.compile("^/+[\w /]+/+$")

# Create your models here.

class Topic(common):

    '''
    A class that holds path for api communications
    
    path - a path to a node aka. (<path>)
    node - a name of a node,topic is referring to
    access - a global access level to topic
    '''

    path=models.CharField(max_length=255,name="path",unique=True,validators=[RegexValidator(regex_path,"String is not a valid path, must be path /.../ ")])
    node=models.CharField(max_length=255,name="node",choices=PublicNodes.get_nodes_list())

    def save(self, *args, **kwargs):

        from common.fetch_api import Fetch

        logging.debug("Subscribed to topics: ")

        if MqttConfig.client is not None:
            for key in Fetch.requests.keys():
                topic=self.path+key
                MqttConfig.client.subscribe(topic)
                logging.debug(topic)
                

        super(Topic, self).save(*args, **kwargs)

    def delete(self, using: Any = DEFAULT_DB_ALIAS, keep_parents: bool = False) -> tuple[int, dict[str, int]]:

        from common.fetch_api import Fetch

        logging.debug("Unsubscribed to topics: ")

        if MqttConfig.client is not None:
            for key in Fetch.requests.keys():
                topic=self.path+key
                MqttConfig.client.unsubscribe(topic)
                logging.debug(topic)

        return super().delete(using, keep_parents)