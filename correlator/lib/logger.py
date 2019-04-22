####################################################
# Styler & Logger
####################################################
from logging.handlers import SysLogHandler
import logging
import json
import time
from decoder import decode
import collections


# Syslog
def syslog(server, port=514, ident='IronPort'):
    address = (server, port)
    facility = SysLogHandler.LOG_LOCAL5
    # Logger
    log = logging.getLogger(ident)
    log.setLevel(logging.INFO)
    # add handler to the logger
    handler = SysLogHandler(address=address, facility=facility)
    # add formatter to the handler
    formatter = logging.Formatter('%(name)s: %(message)r')
    handler.setFormatter(formatter)
    log.addHandler(handler)
    # return
    return log


def style(message):
    result = []
    recipients = message.get('To', [])
    message_log = collections.OrderedDict()

    # Order
    keys = ['ICID', 'MID' , "MessageID", 'NewMID', 'OldMID',
            # 'Rewrite_By', 'Generated_By', 'Generated_By_Filter'
            'OutbreakFilters', 'CASE', 'GRAYMAIL', 'Antivirus', 'LDAP_Drop',
            'SPF' ,'DKIM', 'DKIM_Detail', 'DMARK', 'DMARK_Detail',
            "Subject", "Attachments", "From", "To",
            "SenderReputation", "ThreatCategory", "SuspectedDomains", "DomainAge",
            'Action', 'Action_Desc', 'Action_Filter', "IP"
            "Other"]

    for key in keys:
        message_log[key] = ' || '.join(list(set(message.get(key, []))))

    # Decode Subject
    message_log["Subject"] = decode(message_log["Subject"])
    message_log["Attachments"] = decode(message_log["Attachments"])

    for recipient in recipients:
        message_log['To'] = recipient
        result.append(json.dumps(message_log))

    return result


def logger(logger_queue, syslog_server):

    print "\t[+]Starting Logger Process"

    # Logger
    log = syslog(syslog_server)

    while True:

        data = logger_queue.get()

        if data:
            [(mid, message)] = data.items()

            # Style
            messages = style(message)

            # Log
            for message in messages:
                log.info(message)
                print message

        else:
            # sleep
            time.sleep(0.05)
