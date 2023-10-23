import paho.mqtt.client as mqtt
from typing import Optional,Any
from django.apps import apps,AppConfig
from typing import Iterator
import logging
import threading

class MqttConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mqtt'
    client:mqtt.Client|None=None
    websocket:threading.Thread|None=None

    def __init__(self, app_name: str, app_module: Optional[Any]) -> None:

        MqttConfig.client=None
        
        super().__init__(app_name, app_module)

    def ready(self) -> None:
        
        from nodes.models import PublicNodes
        from .models import Topic

        import mqtt.mqtt as mqtt

        from devices.websocket import server,run_websocket

        try:

            nodes_list=PublicNodes.get_nodes_list()

            Topic.node.choices=nodes_list

            logging.debug("mqtt: "+str(nodes_list))

            MqttConfig.client=mqtt.create_client()

            MqttConfig.client.loop_start()
        except Exception as e:
            logging.error("Cannot run mqtt!")
            logging.debug("MQTT exception: "+str(e))

        try:

            MqttConfig.websocket=run_websocket()

            MqttConfig.websocket.start()
        except Exception as e:
            logging.error("Cannot run websocket!")
            logging.debug("Websocket exception: "+str(e))

        return super().ready()