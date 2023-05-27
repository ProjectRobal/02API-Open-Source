from typing import Optional,Any
from django.apps import apps,AppConfig
from typing import Iterator
import logging

class MqttConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mqtt'

    def __init__(self, app_name: str, app_module: Optional[Any]) -> None:
        
        super().__init__(app_name, app_module)

    def ready(self) -> None:

        import mqtt.mqtt as mqtt

        client=mqtt.create_client()

        client.loop_start()

        return super().ready()