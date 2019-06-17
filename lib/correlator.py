################################################################################
# Read & Send, All Log Messages
################################################################################
import re
import json
import redis
import time
from collections import OrderedDict


# redis
pipe = redis.Redis()


def mid_with_epoch(mid):
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


def correlator(redis_key):
    '''
    A worker that read log message from redis server, then:
        1- Get mid,
        2- Look for mid:epoch in redis, if no create it.
        3- Push the MID:EPOCH = {'key1':[match1, match2], 'key2':[match3]} to redis
    '''
    print("\t[+]Starting Parser Process")

    while True:
        # Get log from redis
        rkey, rawlog = pipe.blpop(redis_key, 0)

        # Extract mid, type
        log = json.loads(rawlog)
        mid = log.get('MID')
        type = log.get('type')

        if type:
            rmid = mid_with_epoch(mid)
            del log['MID']

            for key, value in log.items():
                pipe.rpush(rmid, json.dumps([key, value]))
