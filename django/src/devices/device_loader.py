'''
A script to load device and it's nodes from archive with:

index.json - a file that describe device
nodes.json - a file that list device's nodes

Example index.json

{

“service_rev”: “1.0” - wersja serwera,

“version”:”1.0” - wersja 02API,

“device_rev”: “1.0.0” - wersja urządzenia,

“node_file”:”nodes.json” - nazwa pliku z nodami, ( domyślnie nodes.json)

“name”: ”dev1” - nazwa urządzenia,

“device_key”:”key” - klucz urządzenia,

“protocols”:[“mqtt”,”http”,”websocket”] - lista wspieranych protokołów,

“topics”: - lista tematów

{

“/topic/serv/”:

{

“node”:”data1”, - nazwa noda do któreg odwołuje się temat,

“acl”: - lista dostępu

{

“ ”:[“get”,”post”,”mod”,”pop”], - “nazwa urządzenia”: “lista z dostępem”,

}

},

}

}

'''

import datetime
import os
from collections import namedtuple
import json
import gzip
import shutil
import logging
from domena.settings import SERVER_VERSION
from common.fetch_api import O2_API_VERSION
from common.acess_levels import Access

from .models import Device
from mqtt.models import Topic
from nodeacl.models import NodeACL

import node_generator

DEVICE_TMP_FILE="tmp/device.tmp"

DEVICE_TMP_ARCHIVE="tmp/dev_unpacked"

# zero two device extension
DEVICE_ARCHIVE_EXTENSION="ztd"

def clean_temporary():
    shutil.rmtree('tmp', ignore_errors=True)

def version_to_number(ver:str)->int:
    '''
    A function that converts version string in format:
    a.b.c into number abc
    returns -1 if string version has invalid format
    '''

    return ver[0]*100+ver[2]*10+ver[4]

def load_device(obj)->Device or None:
    '''
    Add device from json from index.json
    '''
    try:


        try:
            dev=Device.objects.get(name=obj["name"])

            if version_to_number(dev.version)<=version_to_number(obj["version"]):
                logging.error("Cannot overwrite device with lesser version")
                return None
                        
        except Device.DoesNotExist:
            dev=Device()

        dev.name=obj["name"]
        dev.key=obj["device_key"]
        dev.version=obj["version"]

        # to do protocols
        
    except:
        logging.error("Device json is invalid!")
        return None

    return dev

def add_topics(topics:dict)->tuple(list[Topic]|None,list[NodeACL]|None):
    paths:list[Topic]=[]
    acls:list[NodeACL]=[]
    try:

        for topic in topics.items():
            path=Topic()
            path.path=topic[0]

            args:dict=topic[1]

            path.node=args["node"]

            acl_list:dict=args["acl"]

            for acl in acl_list.items():
                for access in acl[1]:
                    _acl=NodeACL()
                    if not acl[0].isspace():
                        _acl.device=Device.objects.get(name=acl[0])
                    else:
                        _acl.device=None
                    _acl.topic=path

                    val:int|None=Access.from_str(access.toupper().strip())

                    if val is None:
                        raise ValueError

                    _acl.access_level=val
                    acls.append(_acl)

            paths.append(path)

        return (paths,acls)
    except (ValueError,Device.DoesNotExist) as e:
        logging.error(str(e))
        return (None,None)

    

def add_device()->bool:

    added_nodes:list[str]=[]
        
    try:
        logging.info("Unpacking the ZTD archive into temporary")
        shutil.unpack_archive(
            filename=DEVICE_TMP_FILE,
            extract_dir=DEVICE_TMP_ARCHIVE,
            format='zip'
        )

        logging.info("Search for index.json")

        # check if meta file exists
        if not os.path.exists(DEVICE_TMP_ARCHIVE+'/index.json'):
            logging.error("No valid index.json file")
            clean_temporary()
            return False
        
        file=open(DEVICE_TMP_ARCHIVE+'/index.json')
                  
        obj=json.load(file)

        if not obj["service_rev"]==SERVER_VERSION:
            logging.error("Server version mismatch")
            clean_temporary()
            return False
        
        if not obj["version"]==O2_API_VERSION:
            logging.error("02API version mismatch")
            clean_temporary()
            return False
        
        dev=load_device(obj)
        
        if dev is None:
            logging.error("Invalid index.json file")
            clean_temporary()
            return False
        
        node_file=obj["node_file"]

        logging.info("Search node file ")

        # check if node file exists
        if not os.path.exists(DEVICE_TMP_ARCHIVE+'/'+node_file):
            logging.error("No valid node file file, cannot find: "+node_file)
            clean_temporary()
            return False
        

        logging.info("Generating node files ")

        # list that stores names of generated nodes
        added_nodes:list[str]=node_generator.node_generator(DEVICE_TMP_ARCHIVE+'/'+node_file)
        
        if len(added_nodes)==0:
            logging.error("No nodes were added")
            clean_temporary()
            return False
        

        logging.info("Adding ACL and topics rules")

        topics=obj["topics"]

        paths,acls=add_topics(topics)

        if paths is None or acls is None:
            logging.error("No topics and acls were added")
            node_generator.purge_nodes(added_nodes)
            clean_temporary()
            return False


        logging.info("Saving device instance")

        dev.save()

        logging.info("Saving topics instance")

        for topic in topics:
            topic.save()

        logging.info("Saving nodes instance")

        for acl in acls:
            if acl.device==None:
                acl.device=dev
            acl.save()

        logging.info("Device has been added!")



    except ValueError as e:
        logging.error("Cannot open archive: "+str(e))
        node_generator.purge_nodes(added_nodes)
        clean_temporary()
        return False