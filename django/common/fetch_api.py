'''
API set for interface between mqtt and sql through django. 

'''
import logging
import json
from django.db import models
from django.forms.models import model_to_dict
from django.core.serializers.json import DjangoJSONEncoder
from nodeacl.models import NodeACL
from devices.models import Device
from .acess_levels import Access
from mqtt.models import Topics


class FetchAuth:
    '''
    A class that will handle authentication of a device.
    '''

    def check(dev_key:str or None,access:list[Access],topic:Topics)->bool:

        try:
        
            device=Device.objects.get(key=dev_key)

            query=NodeACL.objects.get(device=device,topic=topic)

            for level in access:
                if query.access_level==level:
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

    def __init__(self,dev_id:str,model:models.Model,acess:Access,topic:Topics) -> None:
        self.model=model
        self.dev_id=dev_id
        self.acess=acess
        self.topic=topic
        self.requests:dict={
            "get":self.get_ex,
            "post":self.post,
            "mod":self.mod,
            "":self.get
        }

    def match(self,request:str,data:dict|None)->FetchResult:
            
            return self.requests.setdefault(request,self.get)(data)
            
    def mod(self,data:dict)->FetchResult:

        if self.acess!=Access.MODIFY:
            return FetchResult(-11,"Node not modifiable")
        
        if not FetchAuth.check(self.dev_id,[Access.MODIFY],self.topic):
            return FetchResult(-11,"Wrong authentications")
        
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

        if self.acess==Access.READ:
            return FetchResult(-10,"Node is read only")
        
        if not FetchAuth.check(self.dev_id,[Access.WRITE,Access.MODIFY],self.topic):
            return FetchResult(-11,"Wrong authentications")

        try:
        
            record=self.model(**data)

            record.save()

            return FetchResult(0,"Entry added!")

        except Exception as e:
            
            return FetchResult(-1,"Entry not added: "+str(e))

    def get(self)->FetchResult:

        if self.dev_id is None and self.acess!=Access.ANYMONUS_READ:
            return FetchResult(-12,"Anynomus reading not allowed")

        if self.model.objects.count()==0:
            return FetchResult(-2,"Database is empty")

        result=self.model.objects.all()[0]

        return FetchResult(0,"Object retrived",model_to_dict(result))
    
    def get_ex(self,data:dict)->FetchResult:

        if self.dev_id is None and self.acess!=Access.ANYMONUS_READ:
            return FetchResult(-12,"Anynomus reading not allowed")
        
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

                if len(mask)!=0:
                    result=result.only(*mask)
                
                if max>0:
                    result=result[:max]

                output:list[dict]=[]

                for res in result:
                    output.append(model_to_dict(res))

                if result.exists():

                    return FetchResult(0,"Objects retrived",
                                       {
                        "data":output
                                       })
                
                else:

                    return FetchResult(-2,"Objects not found")




            

        
        



        


