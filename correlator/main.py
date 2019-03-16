#!/usr/bin/python
#################################################################
# Main Process
##################################################################
from multiprocessing import Manager, Process, Queue, Value
from lib import logger, parser, monitor
import sys
import os.path
import time


# Vars,
log_server = "10.100.251.75"

# Sys path
sys.path.append(os.path.realpath(__file__))

# Shared Objects
manager = Manager()
status_list = manager.dict()

# Queues
logger_queue = Queue()


# Start Query Process
parser_process = Process(
    target=parser, args=())
parser_process.daemon = True
parser_process.start()


# Start Monitor Process
monitor_process = Process(
    target=monitor, args=(logger_queue, ))
monitor_process.daemon = True
monitor_process.start()


# Start Loggger Process
logger_process = Process(
    target=logger, args=(logger_queue, log_server))
logger_process.daemon = True
logger_process.start()


# Join
parser_process.join()
monitor_process.join()
logger_process.join()
