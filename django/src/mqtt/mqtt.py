import json
import paho.mqtt.client as mqtt
from domena import settings
from .models import Topic,TopicCatcher
from common.fetch_api import Fetch
import logging
from .models import PublicNodes

def subscribe_to_topics(mqtt_client:mqtt.Client):


    topics=Topic.objects.all()

    if topics.exists():
        logging.debug("Nodes topics: ")
        for node in topics:

            for req in Fetch.requests.keys():
                topic:str=node.path+"/"+req
                mqtt_client.subscribe(topic)
                logging.debug(topic)

        # there is no need to further
        return
    else:
        logging.error("No valid topics has been found!")

    catcher=TopicCatcher.objects.all()

    if catcher.exists():
        logging.debug("Topics to catch: ")
        for node in catcher:
            mqtt_client.subscribe(node.path)
            logging.debug("Listenning to: "+node.path)


def on_connect(mqtt_client, userdata, flags, rc):
    if rc == 0:
        logging.debug('Connected successfully')        
        subscribe_to_topics(mqtt_client)
    else:
        logging.debug('Bad connection. Code:', rc)

def on_message(mqtt_client:mqtt.Client, userdata, msg:mqtt.MQTTMessage):
   
    try:
   
        logging.debug(f'Received message on topic: {msg.topic} with payload: {msg.payload}')

        # mqtt catcher:

        msg.topic=msg.topic.replace('\\' , "/").encode()

        if not isinstance(msg.payload,str):
            msg.payload=msg.payload.decode('utf-8')

        try:

            catcher=TopicCatcher.objects.get(path=msg.topic)

            node:PublicNodes=PublicNodes.get_obj(catcher.node)

            if node is not None:
                model=node(**json.loads(msg.payload))

                model.save()

                logging.info("Data saved from topic: "+msg.topic+" to node "+catcher.node)
                mqtt_client.subscribe(catcher.path)
                return
         
        except TopicCatcher.DoesNotExist:
            logging.debug("Cannot find topic in topic catcher, trying with fetch api")
   
        topic:str=msg.topic

        logging.debug("Topic: "+topic)

        paths:list[str]=topic.rpartition("/")
        
        # fetch api:

        try:

            check=Topic.objects.get(path=paths[0])

        except Topic.DoesNotExist:
            logging.debug("Topic not found")
            return
   
        mqtt_client.subscribe(topic)
   
        cmd:str=paths[2]

        logging.debug("Found command: "+cmd)
   
        data:dict=json.loads(msg.payload)

        key=None

        if "key" in data:
               key=data["key"]
    
        if "data" in data:
               data=data["data"]
        else:
               data={}

        if key is not None:

            fetch=Fetch(key,PublicNodes.get_obj(check.node),check)

            result=fetch.match(cmd,data)

            dev=fetch.getDevice()
            
            if dev is not None:
                # return data
                return_topic:str="/devs/"+dev.name+"/output"
                mqtt_client.publish(return_topic,str(result))

                logging.debug("Answer at: "+return_topic)
                logging.debug("With result: "+str(result))
            else:
                logging.error("Invalid device key!")
        else:
               logging.debug("No key or output provided!")

    except Exception as e:
            logging.error("I się wywalił")
            logging.debug(str(e))

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