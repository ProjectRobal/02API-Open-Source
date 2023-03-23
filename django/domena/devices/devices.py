import uuid
from django.db import models

class Device(models.Model):
    '''
    name - name of the device
    register_date - a date when device was registered
    last_login_date - a date when device was last logged in
    '''
    id=models.UUIDField(default=uuid.uuid4,
                                primary_key=True,
                               editable=False,
                               unique=True)
    name= models.CharField(max_length=64)
    register_date= models.DateTimeField(blank=True,null=True)
    last_login_date=models.DateTimeField(blank=True,null=True)

    def __str__(self):
        return self.name