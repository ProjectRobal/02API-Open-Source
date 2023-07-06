import logging
import os

import os
import logging

logging.info("Loading generated nodes")

for entry in os.scandir('/app/nodes/imported/'):
	if entry.is_file() and entry.name!="__init__.py":
        
		if entry.name.rpartition(".")[2]=='py':
			exec(open(entry.path).read())