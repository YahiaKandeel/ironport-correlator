################################################################################
# Styler & Logger
################################################################################
from logging.handlers import SysLogHandler
import logging
import json
import pprint
import time
from .decoder import decode
import collections


# Log Keys Order
keys = [
    'ICID', 'MID', "MessageID", 'Related_MID',
    'OutbreakFilters', 'CASE', 'GRAYMAIL', 'Antivirus', 'LDAP_Drop',
    'SPF', 'DKIM', 'DKIM_Detail', 'DMARK', 'DMARK_Detail',
    "Subject", "Attachments", "From", "To",
    "SenderReputation", "ThreatCategory", "SuspectedDomains", "DomainAge",
    'Action', 'Action_Desc', 'Content_Filter', "IP", "Other"
]


# Syslog
def syslog(siemContext):
    '''
        Return a syslogger instance
    '''
    # Create Handler
    handler = SysLogHandler(address=(siemContext["server"], siemContext["port"]),
                            facility=SysLogHandler.LOG_LOCAL5)

    # Configure Logger
    logger = logging.getLogger(siemContext["ident"])
    logger.setLevel(logging.INFO)

    # Configure Formater
    formatter = logging.Formatter('%(name)s: %(message)r')
    handler.setFormatter(formatter)

    # Add handler to the logger
    logger.addHandler(handler)
    # return
    return logger


def style(message, msgexpand):
    '''
        Style and expand a message
    '''
    message_log = collections.OrderedDict()
    result = []

    for key in keys:
        values = filter(None, message.get(key, []))
        message_log[key] = ' || '.join(list(set(values)))

    # Decode Subject & Attachments
    message_log["Subject"] = decode(message_log["Subject"])
    # message_log["Attachments"] = decode(message_log["Attachments"])

    # If msgexpand
    if msgexpand:
        for recipient in message.get('To', []):
            message_log['To'] = recipient
            result.append(
                json.dumps(message_log, ensure_ascii=False))
    # Else
    else:
        result.append(
            json.dumps(message_log, ensure_ascii=False))

    return result


def syslogger(logger_queue, siemContext, options):
    '''
        Logger Process
    '''
    print("\t[+]Starting Logger Process")
    # Logger
    logger = syslog(siemContext)
    while True:
        # Get Data from Logger Queue
        data = logger_queue.get()
        # If there is a message
        if data:
            [(mid, message)] = data.items()
            # Style It
            messages = style(message, options["expand"])
            # Log
            for message in messages:
                logger.info(message)
                print('\r\n'+'#' * 100)
                pprint.pprint(json.loads(message))
        else:
            # sleep
            time.sleep(0.05)
