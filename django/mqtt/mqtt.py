import json
import paho.mqtt.client as mqtt
from django.forms.models import model_to_dict
from domena import settings
from .models import Topics
from devices.models import Device
from common.fetch_api import Fetch,FetchResult
import logging

def subscribe_to_topics(mqtt_client:mqtt.Client):
    
    devices=Device.objects.all()

    # devices basic informations
    if devices.exists():

        for dev in devices:
            
            mqtt_client.subscribe("/"+settings.ROOT_API_PATH+"/"+dev.name)
    
    else:
        logging.error("No devices has been found!")

    topics=Topics.objects.all()

    if topics.exists():

        for topic in topics:

            for req in Fetch.requests:
                mqtt_client.subscribe("/"+settings.ROOT_API_PATH+"/"+topic.device+"/"+topic.path+"/"+req)
    
    else:
        logging.error("No valid topics has been found!")
    

def on_connect(mqtt_client, userdata, flags, rc):
    if rc == 0:
        print('Connected successfully')        
        subscribe_to_topics(mqtt_client)
    else:
        print('Bad connection. Code:', rc)

def on_message(mqtt_client:mqtt.Client, userdata, msg:mqtt.MQTTMessage):
   
   print(f'Received message on topic: {msg.topic} with payload: {msg.payload}')
   
   topic:str=msg.topic

   paths:list[str]=topic.split('/')

   if len(paths)==0:
       return
   
   if paths[0]!=settings.ROOT_API_PATH:
       return
   
   if len(paths)==2:
       device=Device.objects.get(name=paths[1])    
       if device.exits():
           # send informations about device
           result=FetchResult(0,"Device informations",model_to_dict(device[0]))


       else:
           # send informations about failure
           pass
       
       return
   
   if not paths[2] in globals:
       return
   
   fetch=Fetch(globals[paths[2]])

   if len(paths)>=3:
       result=fetch.match(paths[3],data)
   else:
       result=fetch.match("",data)
   
   # return data
   mqtt_client.publish(topic+"/"+msg.mid,str(result))

   # subscribe to another message
   mqtt_client.subscribe(topic)
   
   data:dict=json.load(msg.payload)

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
