'''
A script to load device and it's nodes from archive with:

index.json - a file that describe device
nodes.json - a file that list device's nodes

Example index.json

{

“version”:”1.0.0” - wersja serwera,

“device_rev”: “1.0.0” - wersja urządzenia,

“name”: ”dev1” - nazwa urządzenia,

“device_key”:”key” - klucz urządzenia,

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

Working of script:

1.Load archive
    - Unpack it
2.Verified it
    - check if required files are presented
    - check if versions are in tact
3.If server version mismatch prompt user about it and ask him to continue:
    - no : abort and remove unpacked files
    - yes : continue
4. Check if device with specified name exits:
    - no : continue
    - yes : ask user about it and ask if he wish to overwrite it only if device has higher version than existing device
5. If so continue
6. Generate nodes
7. Add appropiate acl records if they don't exist
8. Prompt user about succesful process

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

from ..devices.models import Device
from mqtt.models import Topic
from nodeacl.models import NodeACL

from . import node_generator

DEVICE_TMP_FILE="tmp/device.tmp"

DEVICE_TMP_ARCHIVE="tmp/dev_unpacked"

# zero two device extension
DEVICE_ARCHIVE_EXTENSION="ztd"


required_index_field:list[str]=['name','version','device_rev','topics']

required_nodes_field:list[str]=['nodes']



def version_to_number(ver:str)->list[int]:
    '''
    A function that converts version string in format:
    a.b.c into list of numbers
    '''

    numbers:list[int]=[int(x) for x in ver.split('.')]

    return numbers

def version_difference(ver1:list[int],ver2:list[int])->list[int]:

    output:list[int]=[]

    for v1,v2 in zip(ver1,ver2):
        output.append(v1-v2)

    return output


def compare_versions(ver1:list[int],ver2:list[int])->int:

    '''
        Return 0 when both versions are the same,
        Return 1 when first verion is ahead of second version
        Return -1 when first version is behind of second version
    '''

    diff=version_difference(ver1,ver2)

    output=0

    for d in diff:
        if d>0:
            output=1
        elif d<0:
            output=-1

    return output

def clean_temporary():
    shutil.rmtree('tmp', ignore_errors=True)

def unpack_and_verify_archive()->[int,str]:
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
            raise ValueError([-1,"No valid index.json file"])
        
        if not os.path.exists(DEVICE_TMP_ARCHIVE+'/nodes.json'):
            logging.error("No valid nodes.json file")
            raise ValueError([-2,"No valid nodes.json file"])
        

        with open(DEVICE_TMP_ARCHIVE+'/index.json','r') as file:
            index:dict=json.load(file)

            for req in required_index_field:
                if not req in index.keys():
                    raise ValueError([-3,"No key in index.json: {}".format(req)])
                
        with open(DEVICE_TMP_ARCHIVE+'/nodes.json','r') as file:
            nodes:dict=json.load(file)

            for req in required_nodes_field:
                if not req in nodes.keys():
                    raise ValueError([-3,"No key in index.json: {}".format(req)])
                
        # check server version
        with open(DEVICE_TMP_ARCHIVE+'/index.json','r') as file:
            index:dict=json.load(file)

            version=version_to_number(index["version"])
            server_version=version_to_number(SERVER_VERSION)

            if compare_versions(version,server_version) != 0:
                return [1,"Device server version and current server version mismatch"]
        

        return [0,"OK"]
        
    except ValueError as e:
        
        clean_temporary()
        if type(e) is list:
            return e
        
        logging.error("Cannot open archive: "+str(e))
        return [-10,"Cannot open archive:"+str(e)]



def load_device(obj)->Device or None:
    '''
    Add device from json from index.json
    '''
    try:

        try:
            dev=Device.objects.get(name=obj["name"])

            if version_to_number(dev.version)<=version_to_number(obj["device_rev"]):
                logging.error("Cannot overwrite device with lesser version")
                return None
                        
        except Device.DoesNotExist:
            dev=Device()

        dev.name=obj["name"]
        if "device_key" in obj.keys():
            dev.key=obj["device_key"]
        dev.version=obj["device_rev"]
        
    except Exception as e:
        logging.error("Device json is invalid!")
        logging.error(str(e))
        return None

    return dev

def add_topics(topics:dict)->tuple[list[Topic]|None,list[NodeACL]|None]:
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
                    if not acl[0].isspace() and len(acl[0])!=0:
                        _acl.device=Device.objects.get(name=acl[0])
                    else:
                        _acl.device=None
                    _acl.topic=path

                    val:int|None=Access.from_str(access.upper().strip())

                    if val is None:
                        raise ValueError

                    _acl.access_level=val
                    acls.append(_acl)

            paths.append(path)

        return (paths,acls)
    except (ValueError,Device.DoesNotExist) as e:
        logging.error(str(e))
        return (None,None)


def remove_device(name:str)->bool:
    try:

        dev:Device=Device.objects.get(name=name)

        dev.delete()

        return True

    except Device.DoesNotExist:
        return False

def purge_device(name:str)->bool:
    '''it should also remove nodes'''
    try:
        dev:Device=Device.objects.get(name=name)

        acls=NodeACL.objects.filter(device=dev)

        for acl in acls:
            if acl.topic is not None:

                #check if topic is referenced by another device
                n_reference:int=NodeACL.objects.filter(topic=acl.topic).exclude(device=dev).count()

                #unless then remove it
                if n_reference==0:
                    logging.debug("Found no reference to topic: "+acl.topic.path+" removing...")
                    acl.topic.delete()
                else:
                    logging.debug("Found reference for topic: "+acl.topic.path+" keeping...")

            acl.delete()

        dev.delete()

        return True

    except Device.DoesNotExist:
        return False
    
def remove_topic(path:str)->bool:
    try:

        topic=Topic.objects.get(path=path)

        acls=NodeACL.objects.filter(topic=topic)

        for acl in acls:
            acl.delete()

        topic.delete()

        return True
    
    except Topic.DoesNotExist:
        return False
    


def add_device()->tuple[bool,str]:

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
            return (False,"No valid index.json file")
        
        file=open(DEVICE_TMP_ARCHIVE+'/index.json')
                  
        obj=json.load(file)

        if not obj["version"]==SERVER_VERSION:
            logging.error("Server version mismatch")
            clean_temporary()
            return (False,"Server version mismatch")
        
        if not obj["device_rev"]==O2_API_VERSION:
            logging.error("02API version mismatch")
            clean_temporary()
            return (False,"02API version mismatch")
        
        dev=load_device(obj)
        
        if dev is None:
            logging.error("Invalid index.json file")
            clean_temporary()
            return (False,"Invalid index.json file")
        
        if "node_file" in obj.keys():
            node_file=obj["node_file"]
        else:
            logging.info("No node_file key switching to default node file")
            node_file="nodes.json"

        logging.info("Search node file ")

        # check if node file exists
        if not os.path.exists(DEVICE_TMP_ARCHIVE+'/'+node_file):
            logging.error("No valid node file file, cannot find: "+node_file)
            clean_temporary()
            return (False,"No valid node file file, cannot find: "+node_file)
        

        logging.info("Generating node files ")

        # list that stores names of generated nodes
        added_nodes:list[str]=node_generator.node_generator(DEVICE_TMP_ARCHIVE+'/'+node_file)
        
        if len(added_nodes)==0:
            logging.error("No nodes were added")
            clean_temporary()
            return (False,"No nodes were added")
        

        logging.info("Adding ACL and topics rules")

        topics=obj["topics"]

        paths,acls=add_topics(topics)

        if paths is None or acls is None:
            logging.error("No topics and acls were added")
            node_generator.purge_nodes(added_nodes)
            clean_temporary()
            return (False,"No topics and acls were added")


        logging.info("Saving device instance")

        dev.save()

        logging.info("Saving topics instance")

        for topic in paths:
            topic.save()

        logging.info("Saving nodes instance")

        for acl in acls:
            if acl.device==None:
                acl.device=dev
            acl.save()

        logging.info("Device has been added!")

        return (True,"Device has been added")

    except ValueError as e:
        logging.error("Cannot open archive: "+str(e))
        node_generator.purge_nodes(added_nodes)
        clean_temporary()
        return (False,"Cannot open archive: "+str(e))