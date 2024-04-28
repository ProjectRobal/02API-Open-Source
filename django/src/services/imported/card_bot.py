from nodes.models import PublicNodes

def service(instance):
    
    output_node=PublicNodes.get_obj("card_out")