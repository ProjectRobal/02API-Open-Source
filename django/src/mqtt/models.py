from django.db import models
from common.acess_levels import Access
from nodes.models import PublicNodes

regex_path='^(?!.*[\\\/]\s+)(?!(?:.*\s|.*\.|\W+)$)(?:[a-zA-Z]:)?(?:(?:[^<>:"\|\?\*\n])+(?:\/\/|\/|\\\\|\\)?)+$'

# Create your models here.

class Topic(models.Model):

    '''
    A class that holds path for api communications
    
    path - a path to a node aka. (<path>)
    node - a name of a node,topic is referring to
    access - a global access level to topic
    '''

    path=models.CharField(max_length=255,name="path",unique=True,primary_key=True)
    node=models.CharField(max_length=255,name="node",choices=PublicNodes.get_nodes_list())