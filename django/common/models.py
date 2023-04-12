import uuid
import datetime
from django.db import models

class common(models.Model):
    '''
    id - object id with uuid format
    creation_date - a object creation date
    modification_date
    '''
    id=models.UUIDField(default=uuid.uuid4,name="id",
                                primary_key=True,
                               editable=False)
    class Meta:
        abstract = True
    