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

“mqtt”: - lista tematów mqtt

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

from .models import Device
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

def add_device()->bool:
        
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
        

        logging.info("Adding ACL rules")

        




    except ValueError as e:
        logging.error("Cannot open archive: "+str(e))
        clean_temporary()
        return False