####################################################
# Read & Parse, All Log Messages
####################################################
import re
import json
import redis
import time
from collections import OrderedDict


# redis
pipe = redis.Redis()
redis_key = 'ironport'

# Regx
regex = OrderedDict([
    # Flow
    (('MID', 'ICID'),
        re.compile("Info: Start MID (\d+) ICID (\d+)$")),
    (('MID', 'IP'),
        re.compile("MID (\d+) to RID .*? \[\('received', 'from .*? \(\[(\d+\.\d+\.\d+\.\d+)\]\)")),
    # queued for delivery
    (('MID', 'Action'),
        re.compile("MID (\d+) (queued for delivery)")),

    #** Filters **
    (('MID', 'Action', 'Action_Desc', 'Content_Filter'),
        re.compile("MID (\d+) enqueued for transfer to centralized (quarantine) [\"\\\']*(.*?)[\"\\\']* \((.*)\)")),
    # Dropped
    (('MID', 'Action', 'Content_Filter'),
        re.compile("MID (\d+) (Dropped) by content filter [\"\'](.*)[\"\'] in the inbound table")),
    # Notify
    (('Related_MID', 'MID', 'Action', 'Content_Filter'),
        re.compile("MID (\d+) was generated based on MID (\d+) by (.*) filter [\"\'](.*)[\"\']")),
    # rewritten
    (('MID', 'Action', 'Related_MID', 'Action_Desc'),
        re.compile("MID (\d+) (rewritten) to MID (\d+) by ([\-\w]+)")),
    # release
    (('MID', 'Related_MID', 'Action_Desc', 'Action'),
        re.compile("MID (\d+) received from the SMA \S+ \(MID originally (\d+)\) on ((release) from .*)")),


    #** Filters **
    # Engines
    (('MID', 'OutbreakFilters'),
        re.compile("MID (\d+) Outbreak Filters: verdict (\w+)")),
    (('MID', 'CASE'),
        re.compile("MID (\d+).*using engine: CASE (.*)")),
    (('MID', 'GRAYMAIL'),
        re.compile("MID (\d+) using engine: GRAYMAIL (.*)")),
    (('MID', 'Antivirus'),
        re.compile("MID (\d+).*interim AV verdict using \w+ (.*)")),
    (("Action", 'MID', "LDAP_Drop"),
        re.compile("(LDAP: Drop) query .* MID (\d+) RID \d* address (.*)")),

    # DMARK
    (('MID', 'DMARK'), re.compile("MID (\d+) DMARC: Verification (\w+)")),
    (('MID', 'DMARK_Detail'),
        re.compile("MID (\d+) DMARC: (Message from domain .*)")),
    (('MID', 'SPF'), re.compile("MID (\d+) SPF: mailfrom identity \S+ (\w+)")),
    (('MID', 'DKIM_Detail', 'DKIM'), re.compile("MID (\d+) DKIM: ((\w+) .*)")),

    # Body
    (('MID', 'Attachments'), re.compile("MID (\d+) attachment [\'\"](.*)[\'\"]")),
    (('MID', 'Subject'), re.compile("MID (\d+) Subject [\'\"](.*)[\'\"]")),
    (('MID', 'MessageID'), re.compile("MID (\d+) Message-ID [\'\"](.*)[\'\"]")),
    (('MID', 'To'), re.compile("MID (\d+) ICID \d+ RID \d+ To: \<(.*)\>")),
    (('MID', 'From'), re.compile("MID (\d+) ICID \d+ From: \<(.*)\>")),


    # SDR
    # 'DomainKey': re.compile("DomainKeys: (.*)")),
    (('MID', "SenderReputation", "ThreatCategory", "SuspectedDomains", "DomainAge"),
    re.compile("MID (\d+) SDR: Consolidated Sender Reputation: (\w+), Threat Category: (N\/A|.*?)[\.\,] (?:Suspected Domain\(s\) : (.*)\. )?Youngest Domain Age: (.*)")),

    # Other
    (('MID', 'Other'), re.compile("MID (\d+) (.*)")),
    ])

def get_mid_epoch(mid):
    '''
        Look for the mid:epoch at the redis ;)
            - if there is a match, return it
            - else; create it and return it.
    '''
    keys = pipe.keys(mid + "*")
    if keys:
        rmid = keys[0]
    else:
        epoch = int(time.time())
        rmid = "%s:%s" % (mid, epoch)
    return rmid


def lpush(data):
    '''
        After parsing the data,
        - get mid
        - look for mid:epoch
        - then push the data json(key, vlaue) with its match to mid:epoch
    '''
    mid = data['MID']
    rmid = get_mid_epoch(mid)

    del data['MID']

    for key, value in data.items():
        pipe.rpush(rmid, json.dumps([key, value]))


def parser():
    '''
    A worker that read log message from redis server, then:
        1- Loop over existing parsers,
        2- Extract MID, and the values and match it with the regex keys
        3- Push the MID:EPOCH = {'key1':[match1, match2], 'key2':[match3]} to redis
    '''
    print ("\t[+]Starting Parser Process")

    while True:
        # Get log from redis
        rkey, log = pipe.blpop(redis_key, 0)
        # Extract Message
        message = json.loads(log)['message']

        # check all available parsers
        for key, regx in regex.items():
            match = regx.findall(message)

            # if parser match;
            if match:
                values = match[0]
                lpush(dict(zip(key, values)))
                break
