import uuid
from django.db import models

class common(models.Model):
    id=models.UUIDField(default=uuid.uuid4,
                                primary_key=True,
                               editable=False,
                               unique=True)
    class Meta:
        abstract = True
    