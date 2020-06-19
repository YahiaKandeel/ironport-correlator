#!/usr/bin/python
################################################################################
# Main Process
################################################################################
from multiprocessing import Manager, Process, Queue, Value
from lib import correlator, monitor, syslogger
import sys
import os
import time

########################
# Environment Vars
########################
# Syslog
syslogServer = str(os.getenv("ENV_SYSLOG_SERVER"))
syslogPort = int(str(os.getenv("ENV_SYSLOG_PORT")))
syslogIdent = str(os.getenv("ENV_SYSLOG_IDENT"))
# Redis
redisKey = str(os.getenv("ENV_REDIS_KEY"))
# Logger Style
timeout = int(str(os.getenv("ENV_TIMEOUT")))
msgexpand = True if os.getenv("ENV_MSG_EXPAND") == "True" else False
# LogLevel
logLevel = os.getenv("ENV_LOGLEVEL")

########################
# Sys path
########################
sys.path.append(os.path.realpath(__file__))
os.environ["PYTHONIOENCODING"] = 'utf-8'

########################
# Shared Objects
########################
manager = Manager()
loggerQueue = Queue()

########################
# Main Process
########################
# Start Query Process
correlate_process = Process(target=correlator, args=(redisKey, ))
correlate_process.daemon = True
correlate_process.start()

# Start Monitor Process
monitor_process = Process(target=monitor, args=(loggerQueue, timeout))
monitor_process.daemon = True
monitor_process.start()

# Start Loggger Process
logger_process = Process(target = syslogger,
                         args = (loggerQueue, syslogServer, syslogPort,
                         syslogIdent,msgexpand))

logger_process.daemon = True
logger_process.start()

# Join
correlate_process.join()
monitor_process.join()
logger_process.join()
