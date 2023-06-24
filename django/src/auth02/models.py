import uuid
from django.db import models


from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.

class O2User(AbstractUser):
    uuid=models.UUIDField(default=uuid.uuid4,
                                primary_key=True,
                               editable=False)
    login=models.CharField(max_length=100)

