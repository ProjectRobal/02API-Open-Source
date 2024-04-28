import uuid
from django.db import models

class common(models.Model):
    '''
    id - object id with uuid format
    creation_date - a object creation date
    modification_date
    '''
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    uuid=models.UUIDField(default=uuid.uuid4,
                                primary_key=True,
                               editable=False)
    class Meta:
        abstract = True

