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
    def __init__(self,code:int,message:str,result=None) -> None:
        self.code=code
        self.message=message
        self.result=result

        logging.debug("code: "+str(self.code)+" msg: "+self.message)
        

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
            "message":self.message
        }

        if self.result is not None:
            output["result"]=self.result

        return json.dumps(output, cls=DjangoJSONEncoder)


class Fetch:

    
    def __init__(self,dev_id:str=None,model:models.Model=None,topic:Topic=None) -> None:
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
            return FetchResult(-11,"Wrong privileges")
        
        if len(data)==0:
            if self.model.objects.count()==0:
                return FetchResult(-2,"Database is empty")

            result=self.model.objects.all()[0]

            copy=model_to_dict(result)

            result.delete()

            return FetchResult(0,"Poped first element",copy)
        
        if 'id' in data.keys():
            try:
                result:models.Model=self.model.objects.get(id=data["id"])

                copy=model_to_dict(result)

                result.delete()

                return FetchResult(0,"Got object by id",copy)
            except:
                return FetchResult(-2,"Object not found!")

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

                    return FetchResult(-2,"Objects not found")
                    

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
            return FetchResult(-11,"Wrong privileges")
        
        to_modify=None
        labels={}

        if 'labels' in data.keys():
            labels=data["labels"]
        else:
            return FetchResult(-1,"No labels field provided")


        if 'id' in data.keys():
            try:
                to_modify=self.model.objects.get(id=data["id"])
            except:
                return FetchResult(-2,"No object with specified id")

        else:
            return FetchResult(-1,"No id provided")
        
        for attr,val in labels.items():
            setattr(to_modify,attr,val)

        to_modify.save()

        return FetchResult(0,"Object modified")


    def post(self,data:dict)->FetchResult:

        if not FetchAuth.check(self.dev_id,Access.POST,self.topic):
            return FetchResult(-11,"Wrong privileges")

        try:
        
            record=self.model(**data)

            record.save()

            return FetchResult(0,"Entry added!")

        except Exception as e:
            
            return FetchResult(-1,"Entry not added: "+str(e))

    def get(self,data:dict)->FetchResult:
        
        if not FetchAuth.check(self.dev_id,Access.GET,self.topic):
            return FetchResult(-11,"Wrong privileges")

        if self.model.objects.count()==0:
            return FetchResult(-2,"Database is empty")

        result=self.model.objects.all()[0]

        return FetchResult(0,"Object retrived",model_to_dict(result))
    
    def get_ex(self,data:dict)->FetchResult:

        if not FetchAuth.check(self.dev_id,Access.GET,self.topic):
            return FetchResult(-11,"Wrong privileges")
        
        if 'id' in data.keys():
            try:
                result=self.model.objects.get(id=data["id"])

                return FetchResult(0,"Got object by id",model_to_dict(result))
            except:
                return FetchResult(-2,"Object not found!")

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
                    return FetchResult(-2,"Objects not found")

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
            
        return FetchResult(-1,"No labels provided")

              
    requests={
        "get":get_ex,
        "post":post,
        "mod":mod,
        "pop":pop,
        "":get 
        }
                    




            

        
        



        


