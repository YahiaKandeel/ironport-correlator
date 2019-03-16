############################################################
# Monitor the lists for timeouts
# Gets data drom data_list then pass it to the logger_queue
############################################################
import collections
import redis
import time
import json


# redis
pipe = redis.Redis()
# Timeout in seconds
timeout = 120


# Time our Keys
def get_timeout_rmids():
    result = []
    # epoch now
    now = int(time.time())
    # all keys
    keys = pipe.keys("*:*")
    # get mid, old epoch
    for key in keys:
        mid, epoch = key.split(":")
        # check
        if now - int(epoch) > timeout:
            result.append(key)
    # return
    return result


# POP rmid's data
def lpop(rmid):
    result = collections.defaultdict(list)
    # get
    data_list = pipe.lrange(rmid, 0, -1)
    # Normalize
    for data in data_list:
        key, value = json.loads(data)
        result[key].append(value)
    # delete
    print "Deleting", rmid
    pipe.delete(rmid)
    # return
    return result


# Monitor Process
def monitor(logger_queue):
    print "\t[+]Starting Monitor Process"

    while True:
        # Get Time out MIDs
        rmids = get_timeout_rmids()

        # Get their data
        for rmid in rmids:
            data = lpop(rmid)
            # MID
            mid, epoch = rmid.split(":")
            data['MID'] = [mid]
            # Log
            logger_queue.put({rmid: data})

        # sleep
        time.sleep(0.01)
