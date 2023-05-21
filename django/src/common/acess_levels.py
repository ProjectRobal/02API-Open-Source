from django.db import models


class Access(models.IntegerChoices):
        ANYMONUS_READ=-1,"ANYMONUS"
        READ=0,"READ"
        WRITE=1,"WRITE"
        MODIFY=2,"MODIFY"