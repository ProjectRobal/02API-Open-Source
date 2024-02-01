'''
A file that generates nodes from json file provided by 
device loader

example nodes file:

{
nodes:[
{
    "NazwaObiektu":
        {
        "verbose":"Nazwa widziana",
        "mono":false,
        "null":false,
        "topic":false,
        "fields": - lista pól noda
        {
        "tekst":{type:"text",max_length:55,blank:true},
        .
        .
        .
        "name":{attributes}
        }
    }
},
...
]
}

'''


import json
import os
import shutil
from common.node_field_type import NODE_FIELDS
import logging

OUTPUT_NODE_PATH="/app/nodes/imported"



class NodeHeader:
    verbose:str
    mono:bool
    null:bool
    topic:bool
    fields:dict

    def __init__(self, **entries):
        self.mono=False
        self.null=False
        self.topic=False

        self.__dict__.update(entries)


def make_node(node_name:str,node:NodeHeader)->str:
    '''
    Function that create node file from
    provided json
    '''

    # string that will be saved into python instance
    buff_str:str="""from django.db import models
import django.contrib.postgres.fields as postgres
from nodes.models import PublicNode,MonoNode,NullNode,BeamerNode
"""

    try:

        superior:str=""

        if node.mono:
            superior=+",MonoNode"
        
        if node.null:
            superior+=",NullNode"

        if node.topic:
            superior+=",BeamerNode"

        buff_str+="class {}(PublicNode{}):\n".format(node_name,superior)

        buff_str+="""   _name="{}"\n""".format(node.verbose)

        #generate model fileds
        for field in node.fields.items():

        
            field_attrs:dict=field[1]
            field_name:str=field[0]
            attrs_str:str=""

            if not field_attrs["type"] in NODE_FIELDS.keys():
                return None 
            
            field_type:str=NODE_FIELDS[field_attrs["type"]]

            del field_attrs["type"]

            for attr in field_attrs.items():
                attrs_str+="""{}={},""".format(attr[0],attr[1])

            buff_str+="""   {}={}({})\n""".format(field_name,field_type,attrs_str)


            return buff_str
        
    except Exception as e:
        logging.error("Nodes: "+str(e))
        return None


def purge_nodes(nodes:list[str]):

    for node in nodes:
        os.remove(OUTPUT_NODE_PATH+"/"+node+".py")

def remove_node(node:str)->bool:
    if os.path.exists(OUTPUT_NODE_PATH+"/"+node+".py"):
        os.remove(OUTPUT_NODE_PATH+"/"+node+".py")
        return True
    return False

def node_generator(file:str)-> list[str]:
    '''
    A function that initialaite loading process

    Returns list of created nodes
    '''

    try:

        file=open(file,"r")

        nodes=json.load(file)["nodes"]

        nodes_list:list[str]=[]

        for node in nodes:
            header:NodeHeader=NodeHeader(**node)
            if make_node(header):
                nodes_list.append(header.name)
            else:
                logging.error("Failed to create node: "+header.name)
                
        file.close()

    except Exception as e:
        logging.error("Error when generating node: "+str(e))
        return []

    return nodes_list