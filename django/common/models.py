import uuid
from django.db import models

class common(models.Model):
    id=models.UUIDField(default=uuid.uuid4,name="id",
                                primary_key=True,
                               editable=False)
    class Meta:
        abstract = True
    