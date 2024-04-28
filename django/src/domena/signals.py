from django.contrib.auth.signals import user_logged_in,user_logged_out,user_login_failed
from django.db.models.signals import post_save
from django.dispatch import receiver

import logging

on_login_callbacks=[]

def on_login_callback(sender,user,request,**kwargs):
    for sig in on_login_callbacks:
        sig(sender,user,request,**kwargs)

on_logout_callbacks=[]

def on_logout_callback(sender,user,request,**kwargs):
    for sig in on_logout_callbacks:
        sig(sender,user,request,**kwargs)

on_login_failed_callbacks=[]

def on_login_failed_callback(sender,credentials,request,**kwargs):
    for sig in on_login_failed_callbacks:
        sig(sender,credentials,request,**kwargs)


user_logged_in.connect(on_login_callback)
user_logged_out.connect(on_logout_callback)
user_login_failed.connect(on_login_failed_callback)

def onLogin(func):
    on_login_callbacks.append(func)

def onLogout(func):
    on_logout_callbacks.append(func)

def onLoginFailed(func):
    on_login_failed_callbacks.append(func)
    

'''
 Here the registers services will listen for incoming Nodes updates
'''
@receiver(post_save)
def my_handler(sender,instance, **kwargs):
    from nodes.models import NodeEntry
    from services.models import ServiceProfile
    
    if isinstance(instance,NodeEntry):
        node_name=sender.get_name()
        logging.debug(f"Executed: {node_name}")
        