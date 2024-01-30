import os
import logging

from django.db import models
from common.models import common

from domena.settings import NODES_IMPORT_PATH

class NodeRefernece(common):
	'''

		A model that holds information about filepath of node file and
		amount of devices that utilize node.

		When ref_number it 0 the NodeReference and file on path is removed 
		from server.

		path is relative to node's import path
	
	'''
	path=models.CharField(max_length=255)
	node_name=models.CharField(max_length=255,unique=True)
	ref_number=models.IntegerField(default=1)



logging.info("Loading generated nodes")

for entry in os.scandir(NODES_IMPORT_PATH):
	if entry.is_file() and entry.name!="__init__.py":
        
		if entry.name.rpartition(".")[2]=='py':
			exec(open(entry.path).read())