'''
API set for interface between mqtt and sql through django. 

'''
import logging
import json
from django.db import models
from django.forms.models import model_to_dict
from django.core.serializers.json import DjangoJSONEncoder

class Access(models.IntegerChoices):
        READ=0,
        WRITE=1,
        MODIFY=2



class FetchAuth:
    '''
    A class that will handle authentication of a device.
    '''
    pass
    def info(self,id):
        pass

    def auth(self,id,passwd):
        pass

    def set_status(self,id):
        pass

    def generate_jwt(self):
        pass

    def logged(self,id)->bool:
        pass


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

    requests=["","get","post","mod"]

    def __init__(self,model:models.Model,acess:Access) -> None:
        self.model=model
        self.acess=acess

    def match(self,request:str,data:dict|None)->FetchResult:
        match request:
            case "post":
                return self.post(data)
            case "get":
                return self.get_ex(data)
            case "mod":
                return self.mod(data)
            case _:
                return self.get()
            
    def mod(self,data:dict)->FetchResult:

        if self.acess!=Access.MODIFY:
            return FetchResult(-11,"Node not modifiable")

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

        try:
        
            record=self.model(**data)

            record.save()

            return FetchResult(0,"Entry added!")

        except Exception as e:
            
            return FetchResult(-1,"Entry not added: "+str(e))

    def get(self)->FetchResult:

        if self.model.objects.count()==0:
            return FetchResult(-2,"Database is empty")

        result=self.model.objects.all()[0]

        return FetchResult(0,"Object retrived",model_to_dict(result))
    
    def get_ex(self,data:dict)->FetchResult:
        
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




            

        
        



        


