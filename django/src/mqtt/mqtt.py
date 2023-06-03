import json
import paho.mqtt.client as mqtt
from domena import settings
from .models import Topic
from common.fetch_api import Fetch
import logging
from .models import PublicNodes


def subscribe_to_topics(mqtt_client:mqtt.Client):


    topics=Topic.objects.all()

    if topics.exists():
        logging.debug("Nodes topics: ")
        for node in topics:

            for req in Fetch.requests.keys():
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

   paths:list[str]=topic.rpartition("/")

   try:

    check=Topic.objects.get(path=paths[0]+"/")

   except Topic.DoesNotExist:
       logging.debug("Topic not found")
       return
   
   mqtt_client.subscribe(topic)
   
   cmd:str=paths[2]

   logging.debug("Found command: "+cmd)
   
   data:dict=json.loads(msg.payload.decode('utf-8'))

   key=None

   if "key" in data:
       key=data["key"]

   if "data" in data:
       data=data["data"]
   else:
       data={}
                 
   fetch=Fetch(key,PublicNodes.get_obj(check.node),check)

   result=fetch.match(cmd,data)

   if key is not None:
    # return data
    mqtt_client.publish(paths[0]+"/"+str(key),str(result))

    logging.debug("Answer at: "+paths[0]+"/"+str(key))
    logging.debug("With result: "+str(result))
   else:
       logging.debug("No key provided!")

   #retrive 

def on_unsubscribe(client, userdata, mid):
    logging.debug("Unsubscribed: ")
    logging.debug("MID : "+str(mid))

def on_subscribe(client, userdata, mid, granted_qos):
    logging.debug("Subscribed: ")
    logging.debug("MID : "+str(mid))

def create_client()->mqtt.Client:
    
    client = mqtt.Client(transport='websockets')
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