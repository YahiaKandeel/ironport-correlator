#!/usr/bin/python
################################################################################
# Main Process
################################################################################
from multiprocessing import Manager, Process, Queue, Value
from lib import correlator, monitor, syslogger
import sys
import os
import time

# Vars
syslog = os.getenv("SYSLOG", '127.0.0.1')
port = 514
redis_key = 'ironport'
ident = 'IronPort'
msgexpand = True
timeout = 30

# Sys path
sys.path.append(os.path.realpath(__file__))
os.environ["PYTHONIOENCODING"] = 'utf-8'

# Shared Objects
manager = Manager()
logger_queue = Queue()

# Start Query Process
correlate_process = Process(target=correlator, args=(redis_key, ))
correlate_process.daemon = True
correlate_process.start()

# Start Monitor Process
monitor_process = Process(target=monitor, args=(logger_queue, timeout))
monitor_process.daemon = True
monitor_process.start()

# Start Loggger Process
logger_process = Process(target=syslogger,
                         args=(logger_queue, syslog, port, ident, msgexpand))
logger_process.daemon = True
logger_process.start()

# Join
correlate_process.join()
monitor_process.join()
logger_process.join()
