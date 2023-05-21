from django.db import models


class Protocols(models.IntegerChoices):
        MQTT=0,"MQTT"
        WEBSCOKET=1,"WEBSOCKET"
        HTTP=2,"HTTP"
