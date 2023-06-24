import uuid
import datetime
from django.db import models

class common(models.Model):
    '''
    id - object id with uuid format
    creation_date - a object creation date
    modification_date
    '''
    uuid=models.UUIDField(default=uuid.uuid4,
                                primary_key=True,
                               editable=False)
    class Meta:
        abstract = True

