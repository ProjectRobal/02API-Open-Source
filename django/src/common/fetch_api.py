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
                }
        
        if self.result is not None:
            output["result"]=self.result
        
        return output
    
    def __str__(self):
        output:dict={
            "code":self.code,
            "message":self.message,
            "node":self.node,
        }

        if self.result is not None:
            output["result"]=self.result

        return json.dumps(output, cls=DjangoJSONEncoder)


class Fetch:

    
    def __init__(self,dev_id:str=None,model:NodeEntry=None,topic:Topic=None) -> None:
        self.model=model
        self.dev_id=dev_id
        self.topic=topic     
    
    def match(self,request:str,data:dict|None)->FetchResult:

        if request in self.requests:
            return self.requests[request](self,data)
        else:
            return self.get(data)
                
    def pop(self,data:dict)->FetchResult:

        if not FetchAuth.check(self.dev_id,Access.POP,self.topic):
            return FetchResult(-11,"Wrong privileges",self.model.get_name())
        
        if len(data)==0:
            if self.model.objects.count()==0:
                return FetchResult(-2,"Database is empty",self.model.get_name())

            result=self.model.objects.all()[0]

            copy=model_to_dict(result)

            result.delete()

            return FetchResult(0,"Poped first element",self.model.get_name(),copy)
        
        if 'id' in data.keys():
            try:
                result:models.Model=self.model.objects.get(id=data["id"])

                copy=model_to_dict(result)

                result.delete()

                return FetchResult(0,"Got object by id",self.model.get_name(),copy)
            except:
                return FetchResult(-2,"Object not found!",self.model.get_name())

        if 'labels' in data.keys():

            if type(data["labels"])==dict:

                conditions:dict=data["labels"]

                max:int=0

                mask:list[str]=[]

                if "max" in data.keys():
                    max=int(data["max"])

                if "mask" in data.keys():
                    if type(data["mask"])==list:
                        mask=data["mask"]

                result:models.QuerySet=self.model.objects.filter(**conditions)

                if not result.exists():

                    return FetchResult(-2,"Objects not found",self.model.get_name())
                    

                if len(mask)!=0:
                    result=result.only(*mask)
                
                if max>0:
                    result=result[:max]

                output:list[dict]=[]

                for res in result:
                    output.append(model_to_dict(res))

                for res in result:
                    res.delete()

                return FetchResult(0,"Objects poped",
                                       {
                        "data":output
                                       })
            
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
                to_modify=self.model.objects.get(id=data["id"])
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

        result=self.model.objects.all()[0]

        return FetchResult(0,"Object retrived",self.model.get_name(),model_to_dict(result))
    
    def get_ex(self,data:dict)->FetchResult:

        if not FetchAuth.check(self.dev_id,Access.GET,self.topic):
            return FetchResult(-11,"Wrong privileges",self.model.get_name())
        
        if 'id' in data.keys():
            try:
                result=self.model.objects.get(id=data["id"])

                return FetchResult(0,"Got object by id",self.model.get_name(),model_to_dict(result))
            except:
                return FetchResult(-2,"Object not found!",self.model.get_name())

        if 'labels' in data.keys():

            if type(data["labels"])==dict:

                conditions:dict=data["labels"]

                max:int=0

                mask:list[str]=[]

                if "max" in data.keys():
                    max=int(data["max"])

                if "mask" in data.keys():
                    if type(data["mask"])==list:
                        mask=data["mask"]

                result=self.model.objects.filter(**conditions)

                if not result.exists():
                    return FetchResult(-2,"Objects not found",self.model.get_name())

                if len(mask)!=0:
                    result=result.only(*mask)
                
                if max>0:
                    result=result[:max]

                output:list[dict]=[]

                for res in result:
                    output.append(model_to_dict(res))

                return FetchResult(0,"Objects retrived",
                                       {
                        "data":output
                                       })
            
        return FetchResult(-1,"No labels provided",self.model.get_name())

              
    requests={
        "get":get_ex,
        "post":post,
        "mod":mod,
        "pop":pop,
        "":get 
        }
                    




            

        
        



        


