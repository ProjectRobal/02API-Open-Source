'''
API set for interface between mqtt and sql through django. 
Version for asyncio.

'''
import logging
import json
from asgiref.sync import sync_to_async
from copy import deepcopy
from datetime import datetime
from django.db import models
from django.forms.models import model_to_dict
from django.core.serializers.json import DjangoJSONEncoder
from nodeacl.models import NodeACL
from devices.models import Device
from .acess_levels import Access
from mqtt.models import Topic
from nodes.models import NodeEntry
from .fetch_api import FetchResult

class AFetchAuth:
    '''
    A class that will handle authentication of a device.
    '''

    async def check(dev_key:str or None,access:Access.choices,topic:Topic)->bool:

        try:
        
            device=await Device.objects.aget(key=dev_key)

            device.last_login_date=datetime.today()

            await sync_to_async(device.save)()

            query=await NodeACL.objects.aget(device=device,topic=topic,access_level=access)

            return True
                
        except (Device.DoesNotExist,NodeACL.DoesNotExist) as error:
            logging.error(str(error))

        
        return False



class AFetch:
    
    def __init__(self,dev_id:str=None,model:NodeEntry=None,topic:Topic=None) -> None:
        self.model=model
        self.dev_id=dev_id
        self.topic=topic     
    
    async def match(self,request:str,data:dict|None)->FetchResult:

        if request in self.requests:
            return await self.requests[request](self,data)
        else:
            return await self.get(data)
                
    async def pop(self,data:dict)->FetchResult:

        if not await AFetchAuth.check(self.dev_id,Access.POP,self.topic):
            return FetchResult(-11,"Wrong privileges",self.model.get_name())
        
        mask:list[str]=[]

        if "mask" in data.keys():
            if type(data["mask"]) is list:
                mask=data["mask"]
        
        if len(data)==0:
            if await self.model.objects.acount() ==0:
                return FetchResult(-2,"Database is empty",self.model.get_name())

            result=await self.model.objects.all()[0]

            output:list[dict]=[]

            async for res in result.values(*mask):
                    output.append(res)

            await result.adelete()

            return FetchResult(0,"Poped first element",self.model.get_name(),output)
        
        if 'id' in data.keys():
            try:
                result:models.QuerySet=await sync_to_async(self.model.objects.filter)(uuid=data["id"])

                output:list[dict]=[]

                async for res in result.values(*mask):
                    output.append(res)

                await result.adelete()

                return FetchResult(0,"Got object by id",self.model.get_name(),output)
            except:
                return FetchResult(-2,"Object not found!",self.model.get_name())

        if 'labels' in data.keys():

            if type(data["labels"]) is dict:

                conditions:dict=data["labels"]

                result:models.QuerySet=await sync_to_async(self.model.objects.filter)(**conditions)

                if not await result.aexists():

                    return FetchResult(-2,"Objects not found",self.model.get_name())
                
                output:list[dict]=[]

                async for res in result.values(*mask):
                    output.append(res)

                await result.adelete()

                return FetchResult(0,"Objects poped",self.model.get_name(),output)
            
    async def mod(self,data:dict)->FetchResult:

        if not await AFetchAuth.check(self.dev_id,Access.MOD,self.topic):
            return FetchResult(-11,"Wrong privileges",self.model.get_name())
        
        to_modify=None
        labels={}

        if 'labels' in data.keys():
            labels=data["labels"]
        else:
            return FetchResult(-1,"No labels field provided",self.model.get_name())


        if 'id' in data.keys():
            try:
                to_modify=await self.model.objects.aget(uuid=data["id"])
            except:
                return FetchResult(-2,"No object with specified id",self.model.get_name())

        else:
            return FetchResult(-1,"No id provided",self.model.get_name())
        
        for attr,val in labels.items():
            setattr(to_modify,attr,val)

        await sync_to_async(to_modify.save)()

        return FetchResult(0,"Object modified",self.model.get_name())


    async def post(self,data:dict)->FetchResult:

        if not await AFetchAuth.check(self.dev_id,Access.POST,self.topic):
            return FetchResult(-11,"Wrong privileges",self.model.get_name())

        try:
        
            record=self.model(**data)

            await sync_to_async(record.save)()

            return FetchResult(0,"Entry added!",self.model.get_name())

        except Exception as e:
            
            return FetchResult(-1,"Entry not added: "+str(e),self.model.get_name())

    async def get(self,data:dict)->FetchResult:
        
        if not await AFetchAuth.check(self.dev_id,Access.GET,self.topic):
            return FetchResult(-11,"Wrong privileges",self.model.get_name())

        if await self.model.objects.acount()==0:
            return FetchResult(-2,"Database is empty",self.model.get_name())

        result=(await sync_to_async(list)(self.model.objects.values()))[0]

        #result=(await self.model.objects.aget()).values()

        return FetchResult(0,"Object retrived",self.model.get_name(),result)
    
    async def get_ex(self,data:dict)->FetchResult:

        if not await AFetchAuth.check(self.dev_id,Access.GET,self.topic):
            return FetchResult(-11,"Wrong privileges",self.model.get_name())
        
        max:int=0

        mask:list[str]=[]

        if "max" in data.keys():
            max=int(data["max"])

        if "mask" in data.keys():
            if type(data["mask"]) is list:
                mask=data["mask"]
        
        if 'id' in data.keys():
            try:
                result=await sync_to_async(self.model.objects.filter)(uuid=data["id"])

                output:list[dict]=[]

                async for res in result.values(*mask):
                    output.append(res)

                return FetchResult(0,"Got object by id",self.model.get_name(),output)
            except (self.model.DoesNotExist,Exception) as e:
                logging.error("Error: "+str(e))
                return FetchResult(-2,"Object not found!",self.model.get_name())

        if 'labels' in data.keys():

            if type(data["labels"])==dict:

                conditions:dict=data["labels"]

                result=await sync_to_async(self.model.objects.filter)(**conditions)

                if not await result.aexists():
                    return FetchResult(-2,"Objects not found",self.model.get_name())
                
                if max>0:
                    result=result[:max]

                output:list[dict]=[]

                async for res in result.values(*mask):
                    output.append(res)

                return FetchResult(0,"Objects retrived",self.model.get_name(),output)

        output:list[dict]=[]    
        
        #result=await sync_to_async(list)(self.model.objects.all())

        async for res in self.model.objects.all().values(*mask)[:max]:
            output.append(res)
            
        return FetchResult(0,"Objects retrived",self.model.get_name(),output)

              
    requests={
        "get":get_ex,
        "post":post,
        "mod":mod,
        "pop":pop,
        "":get 
        }
