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
from common.utils import version_to_number,version_difference,compare_versions

from devices.models import Device
from mqtt.models import Topic,TopicCatcher,TopicBeamer
from nodeacl.models import NodeACL

from importer.models import NodeRefernece
import importer.node_generator as node_generator

DEVICE_TMP_FILE="/tmp/device.tmp"

DEVICE_TMP_ARCHIVE="/tmp/dev_unpacked"

# zero two device extension
DEVICE_ARCHIVE_EXTENSION="ztd"


required_index_field:list[str]=['name','version','device_rev','topics']

required_nodes_field:list[str]=['nodes']

'''

Device load sequence:

unpack_and_verify_archive() - / upload REST topic
 ask a prompt if user want to add device with some error messgaes
add_device() - / add_device REST topic

generate_nodes() -
generate_acl_and_topics() - / add_device2 REST topic

# on failure:
    remove_device()


maybe sperate nodes and device importing

Device remove sequence:
remove_device()
remove_device_associated_nodes()
remove_topics_associated_with_removed_nodes()

'''





def clean_temporary():
    shutil.rmtree('tmp', ignore_errors=True)



def check_if_newer_ver_of_device_exits(obj)->(int,str):
    
    try:
        
        dev_ver:list[int]=version_to_number(obj["device_rev"])
        
        try:
        
            dev=Device.objects.get(name=obj["name"])

            curr_dev_ver:list[int]=dev.version_int_list()
            
            ver=compare_versions(dev_ver,curr_dev_ver)
                    
            if ver<0:
                return -2,"Newer instance of device aleardy exists!"
            elif ver == 0:
                return -3,"Device aleardy exists!"
        
        except Device.DoesNotExist:
            return 0,"OK"
        
    except Exception as e:
        logging.error("Device json is invalid!")
        logging.error(str(e))
        return -10,"Invalid device json!"


def load_device(obj)->Device|None:
    '''
    Add device from json in index.json, if device aleardy exist it will be overwritten
    '''
    try:

        dev_ver:list[int]=version_to_number(obj["device_rev"])

        try:
            dev=Device.objects.get(name=obj["name"])
                        
        except Device.DoesNotExist:
            dev=Device()

        dev.name=obj["name"]
        if "device_key" in obj.keys():
            dev.key=obj["device_key"]

        dev.major_version=dev_ver[0]
        dev.minor_version=dev_ver[1]
        dev.patch_version=dev_ver[2]
        
    except Exception as e:
        logging.error("Device json is invalid!")
        logging.error(str(e))
        return None

    return dev


def unpack_and_verify_archive()->(int,str):
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
            raise ValueError((-1,"No valid index.json file"))
        
        if not os.path.exists(DEVICE_TMP_ARCHIVE+'/nodes.json'):
            logging.error("No valid nodes.json file")
            raise ValueError((-2,"No valid nodes.json file"))
        

        with open(DEVICE_TMP_ARCHIVE+'/index.json','r') as file:
            index:dict=json.load(file)

            for req in required_index_field:
                if not req in index.keys():
                    raise ValueError((-3,"No key in index.json: {}".format(req)))
                
        with open(DEVICE_TMP_ARCHIVE+'/nodes.json','r') as file:
            nodes:dict=json.load(file)

            for req in required_nodes_field:
                if not req in nodes.keys():
                    raise ValueError((-3,"No key in index.json: {}".format(req)))
                
        # check server version
        with open(DEVICE_TMP_ARCHIVE+'/index.json','r') as file:
            index:dict=json.load(file)

            version=version_to_number(index["version"])
            server_version=version_to_number(SERVER_VERSION)

            if compare_versions(version,server_version) != 0:
                return (1,"Device server version and current server version mismatch")
    

        return (0,"OK")
        
    except ValueError as e:
        
        clean_temporary()
        if type(e) is list:
            return e
        
        logging.error("Cannot open archive: "+str(e))
        return (-10,"Cannot open archive:"+str(e))


def generate_nodes()->[int,str]:

    try:
    
        with open(DEVICE_TMP_ARCHIVE+'/nodes.json','r') as file:
                nodes:dict=json.load(file)["nodes"]

                create_node=False
                
                for node in nodes.keys():
                    
                    node_path:str=node_generator.OUTPUT_NODE_PATH+"/"+node+".py"
                    # check if node with the same name exits

                    try:
                        
                        ref:NodeRefernece=NodeRefernece.objects.get(node_name=node)

                        ref.ref_number+=1
                                        
                        create_node=True

                    except NodeRefernece.DoesNotExist:
                        # generate node if not exist

                        ref=NodeRefernece()

                        ref.ref_number=1
                        ref.node_name=node
                        ref.path=node_path
                        create_node=True
                    
                    if create_node:
                        node_buff:str=node_generator.make_node(node,node_generator.NodeHeader(**nodes[node]))

                        if node_buff is None:
                            raise ValueError([-5,"Error in generating node text"])

                        if node_path is None:
                            raise ValueError([-4,"Error in node generation!"])

                        file=open(node_path,"w+")

                        file.write(node_buff)

                        file.close()
                    
                    ref.save()
                    
    except ValueError as e:
        clean_temporary()
        
        logging.error("Cannot generate nodes: "+str(e))
        return [-10,"Cannot generate nodes:"+str(e)]
    
    return [0,"OK"]



def add_topics()->tuple[list[Topic]|None,list[NodeACL]|None]:
    paths:list[Topic]=[]
    acls:list[NodeACL]=[]
    
    try:
        
        with open(DEVICE_TMP_ARCHIVE+"/index.json","r") as file:
            
            topics=json.load(file)["topics"]
        
    except:
        logging.error("Cannot open topics section of index.json")
        return None,None
    
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



# device removed related functions:


def remove_device(name:str)->bool:
    try:

        dev:Device=Device.objects.get(name=name)

        dev.delete()
        
        dev.uuid=None
        
        dev.save(using="trashbin")

        return True

    except Device.DoesNotExist:
        return False


def remove_node(reference:NodeRefernece):
    
    os.remove(reference.path)
    logging.info("Removing node file at path "+str(reference.path))
    
    topics=Topic.objects.filter(node=reference.node_name)
    catchers=TopicCatcher.objects.filter(node=reference.node_name)
    beamers=TopicBeamer.objects.filter(node=reference.node_name)
    
    for topic in topics:
        topic.delete()
        
        logging.info("Removing topic "+str(topic.path)+" of node "+str(reference.node_name))
        
    for topic in catchers:
        topic.delete()
        
        logging.info("Removing topic "+str(topic.path)+" of node "+str(reference.node_name))
        
    for topic in beamers:
        topic.delete()
        
        logging.info("Removing topic "+str(topic.path)+" of node "+str(reference.node_name))
    
        
        

def purge_device(id:str)->bool:
    '''it should also remove nodes'''
    try:
        dev:Device=Device.objects.get(uuid=id)

        acls=NodeACL.objects.filter(device=dev)
        
        used_nodes:set[str]=set()
        
        for acl in acls:
            if acl.topic is not None:
                used_nodes.add(acl.topic.node)
            
            logging.debug("Removing Node ACL for device with name: "+str(dev.name))
            acl.delete()

        for node in used_nodes:
            try:
                reference=NodeRefernece.objects.get(node_name=node)
                
                reference.ref_number=reference.ref_number-1
                logging.error("Node reference decreased for node "+str(reference.node_name))
                
                if reference.ref_number == 0:
                    remove_node(reference)
                    reference.delete()
                else:
                    reference.save()
                
            except NodeRefernece.DoesNotExist:
                logging.error("Cannot find reference for node: "+str(node))
            
        dev.delete()

        return True

    except Device.DoesNotExist:
        return False
    

def gen_device()->[int,str,Device|None]:
    
    try:
        with open(DEVICE_TMP_ARCHIVE+"/index.json","r") as file:
            
            obj=json.load(file)
            dev:Device|None=load_device(obj)
            
            if dev is not None:
                
                return [0,"OK",dev]
    except:
        
        return [-15,"Failed to open index.json file",None]
        
    return [-16,"Failed to add device, device aleardy exits",None]


def check_device_ver()->tuple[int,str]:
    
    try:
        with open(DEVICE_TMP_ARCHIVE+"/index.json","r") as file:
            
            obj=json.load(file)
            
            return check_if_newer_ver_of_device_exits(obj)
        
    except:
        
        return -11,"Cannot open index.json file!"