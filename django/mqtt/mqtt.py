import json
import paho.mqtt.client as mqtt
from django.forms.models import model_to_dict
from domena import settings
from .models import Topics
from devices.models import Device
from common.fetch_api import Fetch,FetchResult
from django.apps import apps
import logging

def subscribe_to_topics(mqtt_client:mqtt.Client):

    topics=Topics.objects.all()

    if topics.exists():
        logging.debug("Nodes topics: ")
        for node in topics:

            for req in Fetch.requests:
                topic:str=node.path+req
                mqtt_client.subscribe(topic)
                logging.debug(topic)
    
    else:
        logging.error("No valid topics has been found!")
    

def on_connect(mqtt_client, userdata, flags, rc):
    if rc == 0:
        logging.debug('Connected successfully')        
        subscribe_to_topics(mqtt_client)
    else:
        logging.debug('Bad connection. Code:', rc)

def on_message(mqtt_client:mqtt.Client, userdata, msg:mqtt.MQTTMessage):
   
   logging.debug(f'Received message on topic: {msg.topic} with payload: {msg.payload}')
   
   topic:str=msg.topic

   logging.debug("Topic: "+topic)

   check=Topics.objects.filter(path=topic.rpartition("/")[0]+"/")

   if not check.exists():
       logging.debug("Topic not found")
       return
   
   mqtt_client.subscribe(topic)

   paths:list[str]=topic.split('/')
   
   cmd:str=paths[-1]

   logging.debug("Found command: "+cmd)
   
   fetch=Fetch(apps.get_model("nodes",check[0].node))

   data:dict=json.loads(msg.payload.decode('utf-8'))
   
   result=fetch.match(cmd,data)
   
   # return data
   mqtt_client.publish(topic+str(msg.mid),str(result))

   logging.debug("Answer at: "+topic+str(msg.mid))

   #retrive 

def create_client()->mqtt.Client:
    
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.username_pw_set(settings.MQTT_USER, settings.MQTT_PASSWORD)
    client.connect(
        host=settings.MQTT_SERVER,
        port=settings.MQTT_PORT,
        keepalive=settings.MQTT_KEEPALIVE
    )

    return client

#client.loop_start()
