'''
API set for interface between mqtt and sql through django. 

'''
import logging
import json
from django.db import models

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

        return json.dumps(output)

class Fetch:

    requests=["","get","post","mod"]

    def __init__(self,model:models.Model) -> None:
        self.model=model

    def match(self,request:str,data:dict|None)->FetchResult:
        match request:
            case "post":
                return self.post(data)
            case "get":
                return self.get_ex(dict)
            case _:
                return self.get()


    def post(self,data:dict)->FetchResult:

        try:
        
            record=self.model(*data)

            record.save()

            return FetchResult(0,"Entry added!")

        except Exception as e:
            
            return FetchResult(-1,"Entry not added: "+str(e))

    def get(self)->FetchResult:

        if self.model.objects.count()==0:
            return FetchResult(-2,"Database is empty")

        result=self.model.objects.all()[0]

        return FetchResult(0,"Object retrived",result)
    
    def get_ex(self,data:dict)->FetchResult:
        
        if "id" in data.keys():
            result=self.model.objects.get(id=data["id"])

            if result.exists():
                return FetchResult(0,"Got object by id",result)
            else:
                return FetchResult(-1,"Object not found!")

        if "labels" in data.keys():

            if type(data["labels"])==dict:

                conditions:dict=data["labels"]

                max:int=0

                mask:list[str]=[]

                if "max" in data.keys():
                    max=int(data["max"])

                if "mask" in data.keys():
                    if type(data["mask"])==list:
                        mask=data["mask"]

                result=self.model.filter(**conditions)

                if len(mask)!=0:
                    result=result.only(*mask)
                
                if max>0:
                    result=result[:max]

                if result.exits():

                    return FetchResult(0,"Objects retrived",result)
                
                else:
                    return FetchResult(-1,"Objects not found")




            

        
        



        


