from django.db import models


class Access(models.IntegerChoices):
        GET=0,"GET"
        POST=1,"POST"
        MOD=2,"MOD"
        POP=3,"POP"