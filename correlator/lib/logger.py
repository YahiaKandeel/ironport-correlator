####################################################
# Styler & Logger
####################################################
from logging.handlers import SysLogHandler
import logging
import json
import pprint
import time
from .decoder import decode
import collections


# Syslog
def syslog(server=None, local_file=None, port=514, ident='IronPort'):
    facility = SysLogHandler.LOG_LOCAL5
    # Logger
    log = logging.getLogger(ident)
    log.setLevel(logging.INFO)

    # add handler to the logger
    if server:
        handler = SysLogHandler(address=(server, port), facility=facility)
        formatter = logging.Formatter('%(name)s: %(message)r')
    elif local_file:
        handler = logging.FileHandler(local_file, encoding='utf-8')
        formatter = logging.Formatter("%(asctime)s %(name)s: %(message)s",
                                    "%Y-%m-%d %H:%M:%S")
    else:
        return False
    handler.setFormatter(formatter)
    log.addHandler(handler)
    # return
    return log


def style(message):
    result = []
    recipients = message.get('To', [])
    message_log = collections.OrderedDict()

    # Order
    keys = ['ICID', 'MID' , "MessageID", 'Related_MID',
            'OutbreakFilters', 'CASE', 'GRAYMAIL', 'Antivirus', 'LDAP_Drop',
            'SPF' ,'DKIM', 'DKIM_Detail', 'DMARK', 'DMARK_Detail',
            "Subject", "Attachments", "From", "To",
            "SenderReputation", "ThreatCategory", "SuspectedDomains", "DomainAge",
            'Action', 'Action_Desc', 'Content_Filter', "IP",
            "Other"]

    for key in keys:
        values = filter(None, message.get(key, []))
        message_log[key] = ' || '.join(list(set(values)))

    # Decode Subject
    message_log["Subject"] = decode(message_log["Subject"])
    # message_log["Attachments"] = decode(message_log["Attachments"])

    for recipient in recipients:
        message_log['To'] = recipient
        result.append(json.dumps(message_log, ensure_ascii = False))

    return result


def logger(logger_queue, syslog_server=None, local_file=None):

    print ("\t[+]Starting Logger Process")

    # Logger
    if syslog_server:
        log = syslog(server=syslog_server)

    if local_file:
        local_log = syslog(local_file=local_file)

    while True:

        data = logger_queue.get()

        if data:
            [(mid, message)] = data.items()

            # Style
            messages = style(message)

            # Log
            for message in messages:
                if syslog_server:
                    log.info(message)
                if local_file:
                    local_log.info(message)
                pprint.pprint(json.loads(message))
        else:
            # sleep
            time.sleep(0.05)
