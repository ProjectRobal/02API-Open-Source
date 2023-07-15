'''

A file with websocket related stuff

'''

import threading
import asyncio
from websockets.server import serve,WebSocketServerProtocol
import json
from common import async_fetch_api
from mqtt.models import Topic,PublicNodes

import logging

async def check_for_topic(path:str)->Topic|None:

    try:

        check=await Topic.objects.aget(path=path)

        return check

    except Topic.DoesNotExist:
        logging.debug("Topic not found")
        return None




async def process_msg(msg:str,topic:Topic)->str:

    #try:

        data:dict=json.loads(msg)

        key=None

        cmd:str=""

        if "cmd" in data:
            cmd=data["cmd"]

        logging.debug("Found command: "+cmd)

        if "key" in data:
            key=data["key"]

        if "data" in data:
            data=data["data"]
        else:
            data={}
                 
        fetch=async_fetch_api.AFetch(key,PublicNodes.get_obj(topic.node),topic)

        result=await fetch.match(cmd,data)

        return str(result)
        '''
    except Exception as e:
        logging.error("I się wywalił")
        logging.debug(str(e))

        return str(async_fetch_api.FetchResult(-12,str(e),topic.node))
    '''



async def handler(ws:WebSocketServerProtocol):
    logging.info("Connection on path: "+ws.path[5:]+" with id: "+str(ws.id))
    topic=await check_for_topic(ws.path[5:])
    if topic is None:
            await ws.send(str(async_fetch_api.FetchResult(-2,"Topic not found","")))
            await ws.close(1001,"Topic not found")

    async for msg in ws:
        #try:
            output:str=await process_msg(msg,topic)
            await ws.send(output)
            '''except Exception as e:
            output:str=str(e)
            await ws.send(output)
            await ws.close(1001,output)
            '''

async def server():
    async with serve(handler, "0.0.0.0",9000) as server:
        await asyncio.Future()

def run_websocket()->threading.Thread:
    logging.debug("Websocket server starting...")
    thread=threading.Thread(target=lambda x: asyncio.run(server()),args=(None,))
    thread.daemon=True

    return thread
    
        

