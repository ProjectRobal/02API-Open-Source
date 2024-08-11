from django.db import models

from nodes.models import PublicNode,MonoNode,BeamerNode,NullNode
from common.models import common

# Create your models here.

class LejUserRecord(PublicNode):
    '''
        A model that holds record in who entered/left basement on specific date
    '''
    name=models.TextField(max_length=32)
    time=models.IntegerField()