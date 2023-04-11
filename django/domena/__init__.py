import sys
import logging

FORMAT = "%(name)-12s %(asctime)s %(levelname)-8s %(filename)s:%(funcName)s %(message)s"

logging.basicConfig(level=logging.DEBUG,format=FORMAT)