from django.db import models
import django.contrib.postgres.fields as postgres
from nodes.models import PublicNode,MonoNode


class SensorBoard(PublicNode):
    _name="sensorboard"

    temperature=models.FloatField()
    humidity=models.FloatField()
    oxygen=models.FloatField()
    dust=models.FloatField()