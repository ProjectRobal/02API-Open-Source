'''

A file with websocket related stuff

'''

import threading
import asyncio
from websockets.server import serve,ServerConnection
from common import fetch_api

import logging


async def handler(ws:ServerConnection):
    for msg in ws:
        pass

async def server():
    async with serve(handler, "",9000) as server:
        await asyncio.Future()

def run_websocket()->threading.Thread:
    logging.debug("Websocket server starting...")
    thread=threading.Thread(target=lambda x: asyncio.run(server()),args=(None,))
    thread.daemon=True

    return thread
    
        

