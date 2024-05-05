from django.db import models
import django.contrib.postgres.fields as postgres
from nodes.models import PublicNode,MonoNode,NullNode,BeamerNode
class DataOne(PublicNode):
   _name="data1"
   tekst=models.CharField(max_length=55,blank=True,)
   numer=models.IntegerField(blank=True,)
