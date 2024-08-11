from django.db import models

from nodes.models import PublicNode,UniqueNode

# Create your models here.

class LejUserRecord(UniqueNode,PublicNode):
    '''
        A model that holds CyberLej user records,
        name should be unique
    '''
    _name="lej_record"
    _unique_fields=["name"]
    
    name=models.CharField(max_length=20)
    miliseconds=models.IntegerField()