from django.db import models

from nodes.models import PublicNode,MonoNode,BeamerNode,NullNode
from common.models import common

# Create your models here.

class LejUserRecord(PublicNode):
    '''
        A model that holds CyberLej user records,
        name should be unique
    '''
    _name="lej_record"
    
    name=models.CharField(max_length=20)
    miliseconds=models.IntegerField()