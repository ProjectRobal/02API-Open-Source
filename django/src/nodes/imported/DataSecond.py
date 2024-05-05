from django.db import models
import django.contrib.postgres.fields as postgres
from nodes.models import PublicNode,MonoNode,NullNode,BeamerNode
class DataSecond(PublicNode,MonoNode):
   _name="data2"
   tekst=models.CharField(max_length=120,blank=True,)
   numer=models.FloatField(blank=True,)
