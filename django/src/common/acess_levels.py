from django.db import models


class Access(models.IntegerChoices):
        GET=0,"GET"
        POST=1,"POST"
        MOD=2,"MOD"
        POP=3,"POP"
        CLS=4,"CLS"

        @classmethod
        def from_str(cls,the_string:str)->int|None:

                for num, string in cls.choices:
                        if string == the_string:
                                return num
                return None
