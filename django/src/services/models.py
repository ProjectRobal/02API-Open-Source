from django.db import models

from common.models import common

'''

 Service is a file with a function:

def service(instance):

instance - is a instance of a node the service is working on

'''

# Create your models here.


class ServiceProfile(common):
    '''

        name - service name
        exec_name - name of a file from which service shall run, exec name will use uuid as filename
        node_name - name of a node service is working on
    '''
    name=models.CharField(max_length=255)
    exec_name=models.CharField(max_length=255)
    node_name=models.CharField(max_length=255,unique=True)
    

