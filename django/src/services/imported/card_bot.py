from nodes.models import PublicNodes
import logging

def service(instance):
    
    logging.info(f"Avaliable nodes: {PublicNodes.get_nodes_list()}")
    
    logging.debug(f"Instance name {instance._name}")
    
    output_node=PublicNodes.get_obj("CardUp")
    if output_node is not None:
        logging.info(f"Run service for {output_node.__name__}")