from nodes.models import PublicNodes
from auth02.models import get_user_by_id
from webadmin.models import get_user_projects

import logging

def service(instance):
    
    logging.info(f"Avaliable nodes: {PublicNodes.get_nodes_list()}")
    
    logging.debug(f"Instance name {instance._name}")
    
    OutputNode=PublicNodes.get_obj("CardUp")
    if OutputNode is not None:
        logging.info(f"Run service for {OutputNode.__name__}")
                
        message=OutputNode()
        message.username=instance.user.username
        message.first_name=instance.user.first_name
        message.second_name=instance.user.last_name
        message.is_in_basement=instance.is_in_basement
        
        projects=[]
        
        for project in get_user_projects(instance.user):
            projects.append(project.project_name)
        
        message.projects=projects
        
        message.save()
        logging.debug("Basement Bot message sent!")