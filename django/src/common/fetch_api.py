'''
API set for interface between mqtt and sql through django. 

'''
import logging
import json
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

# 02 api version
O2_API_VERSION="1.0"

class FetchAuth:
    '''
    A class that will handle authentication of a device.
    '''

    def check(dev_key:str or None,access:Access.choices,topic:Topic)->bool:
        
        if dev_key is None:
            # add permission check for user?
            return True

        try:
        
            device=Device.objects.get(key=dev_key)

            device.last_login_date=datetime.today()

            device.save()

            query=NodeACL.objects.get(device=device,topic=topic,access_level=access)

            return True
                
        except (Device.DoesNotExist,NodeACL.DoesNotExist) as error:
            logging.error(str(error))

        
        return False


class FetchResult:
    def __init__(self,code:int,message:str,node:str,result=None) -> None:
        self.code=code
        self.message=message
        self.result=result
        self.node=node

        logging.debug("code: "+str(self.code)+" from node: "+node+" msg: "+self.message)
        

    def __bool__(self):
        return self.result!=None
    
    def __dict__(self):

        output:dict={
                "code":self.code,
                "message":self.message,
                "node":self.node
                }
        
        if self.result is not None:
            logging.debug("Result: "+str(self.result))
            output["result"]=self.result
        
        return output
    
    def __str__(self):

        return json.dumps(self.__dict__(), cls=DjangoJSONEncoder)


class Fetch:
    
    def __init__(self,dev_id:str=None,model:NodeEntry=None,topic:Topic=None) -> None:
        self.model=model
        self.dev_id=dev_id
        self.topic=topic    

    def getDevice(self)->Device|None:
        try:

            return Device.objects.get(key=self.dev_id)

        except Device.DoesNotExist:
            return None 
    
    def match(self,request:str,data:dict|None)->FetchResult:

        request=request.lower()

        if request in self.requests:
            return self.requests[request](self,data)
        else:
            return self.get(data)
                
    def pop(self,data:dict)->FetchResult:

        if not FetchAuth.check(self.dev_id,Access.POP,self.topic):
            return FetchResult(-11,"Wrong privileges",self.model.get_name())
        
        mask:list[str]=[]

        if "mask" in data.keys():
            if type(data["mask"])==list:
                mask=data["mask"]
        
        if len(data)==0:
            if self.model.objects.count()==0:
                return FetchResult(-2,"Database is empty",self.model.get_name())

            result=self.model.objects.all()

            output:list[dict]=[]

            output.append(result.values(*mask)[0])

            result[0].delete()

            return FetchResult(0,"Poped first element",self.model.get_name(),output)
        
        if 'id' in data.keys():
            try:
                result:models.Model=self.model.objects.filter(uuid=data["id"])

                output:list[dict]=[]

                for res in result.values(*mask):
                    output.append(res)

                result.delete()

                return FetchResult(0,"Got object by id",self.model.get_name(),output)
            except:
                return FetchResult(-2,"Object not found!",self.model.get_name())

        if 'labels' in data.keys():

            if type(data["labels"])==dict:

                conditions:dict=data["labels"]

                result:models.QuerySet=self.model.objects.filter(**conditions)

                if not result.exists():

                    return FetchResult(-2,"Objects not found",self.model.get_name())

                output:list[dict]=[]

                for res in result.values(*mask):
                    output.append(res)

                result.delete()

                return FetchResult(0,"Objects poped",self.model.get_name(),output)
            
    def mod(self,data:dict)->FetchResult:

        if not FetchAuth.check(self.dev_id,Access.MOD,self.topic):
            return FetchResult(-11,"Wrong privileges",self.model.get_name())
        
        to_modify=None
        labels={}

        if 'labels' in data.keys():
            labels=data["labels"]
        else:
            return FetchResult(-1,"No labels field provided",self.model.get_name())


        if 'id' in data.keys():
            try:
                to_modify=self.model.objects.get(uuid=data["id"])
            except:
                return FetchResult(-2,"No object with specified id",self.model.get_name())

        else:
            return FetchResult(-1,"No id provided",self.model.get_name())
        
        for attr,val in labels.items():
            setattr(to_modify,attr,val)

        to_modify.save()

        return FetchResult(0,"Object modified",self.model.get_name())


    def post(self,data:dict)->FetchResult:

        if not FetchAuth.check(self.dev_id,Access.POST,self.topic):
            return FetchResult(-11,"Wrong privileges",self.model.get_name())

        try:
        
            record=self.model(**data)

            record.save()

            return FetchResult(0,"Entry added!",self.model.get_name())

        except Exception as e:
            
            return FetchResult(-1,"Entry not added: "+str(e),self.model.get_name())

    def get(self,data:dict)->FetchResult:
        
        if not FetchAuth.check(self.dev_id,Access.GET,self.topic):
            return FetchResult(-11,"Wrong privileges",self.model.get_name())

        if self.model.objects.count()==0:
            return FetchResult(-2,"Database is empty",self.model.get_name())

        result=self.model.objects.all().values()[0]

        return FetchResult(0,"Object retrived",self.model.get_name(),result)
    
    def get_ex(self,data:dict)->FetchResult:

        if not FetchAuth.check(self.dev_id,Access.GET,self.topic):
            return FetchResult(-11,"Wrong privileges",self.model.get_name())
        
        max:int=0

        mask:list[str]=[]

        if "max" in data.keys():
            max=int(data["max"])

        if "mask" in data.keys():
            if type(data["mask"])==list:
                mask=data["mask"]
                logging.debug("Using mask of: "+str(mask))
        
        if 'id' in data.keys():
            try:
                result=self.model.objects.filter(uuid=data["id"]).values(*mask)

                output:list[dict]=[]

                for res in result:
                    output.append(res)

                return FetchResult(0,"Got object by id",self.model.get_name(),output)
            except:
                return FetchResult(-2,"Object not found!",self.model.get_name())

        if 'labels' in data.keys():

            if type(data["labels"])==dict:

                conditions:dict=data["labels"]

                result=self.model.objects.filter(**conditions)

                if not result.exists():
                    return FetchResult(-2,"Objects not found",self.model.get_name())
                
                if max>0:
                    result=result[:max]

                output:list[dict]=[]

                for res in result.values(*mask):
                    output.append(res)

                return FetchResult(0,"Objects retrived",self.model.get_name(),output)

        output:list[dict]=[]    
        
        result=self.model.objects.all()
        
        if "order" in data.keys():
            logging.debug("Ordered by "+data["order"])
            result=result.order_by(data["order"])

        if max<=0:
            max=len(result)

        for res in result.values(*mask)[:max]:
            output.append(res)
            
        return FetchResult(0,"Objects retrived",self.model.get_name(),output)

              
    requests={
        "get":get_ex,
        "post":post,
        "mod":mod,
        "pop":pop,
        "":get 
        }
                    




            

        
        



        


