import sys
import os
import logging

FORMAT = "%(name)-12s %(asctime)s %(levelname)-8s %(filename)s:%(funcName)s %(message)s"

if os.environ.get("DJANGO_MODE")=='DEBUG':
    logging.basicConfig(level=logging.DEBUG,format=FORMAT)
else:
    logging.basicConfig(level=logging.INFO,format=FORMAT)