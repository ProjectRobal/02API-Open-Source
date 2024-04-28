from nodes.models import PublicNodes
import logging

def service(instance):
    
    output_node=PublicNodes.get_obj("card_up")
    logging.info(f"Run service for {output_node.get_name()}")
    