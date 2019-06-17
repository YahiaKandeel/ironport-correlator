################################################################################
# Monitor the lists for timeouts
# Gets data drom data_list then pass it to the logger_queue
################################################################################
import collections
import redis
import time
import json

# redis
pipe = redis.Redis()


# Time our Keys
def get_timeout_rmids(timeout):
    '''
        Input: timout
        Operation: Loop through redis keys, then return the timed out ones.
    '''
    result = []
    now = int(time.time())
    keys = pipe.keys("*:*")
    # Iterate over all keys
    for key in keys:
        mid, epoch = key.decode().split(":")
        # Check for expirations
        if now - int(epoch) > timeout:
            result.append(key)
    return result


# POP rmid's data
def lpop(rmid):
    '''
        Return all data associated with a Key (rmid)
    '''
    result = collections.defaultdict(list)
    data_list = pipe.lrange(rmid, 0, -1)
    for data in data_list:
        key, value = json.loads(data)
        result[key].append(value)
    return result


# Monitor Process
def monitor(logger_queue, timeout):
    print("\t[+]Starting Monitor Process")

    while True:
        # Get Time out MIDs
        rmids = get_timeout_rmids(timeout)

        # Get their data
        for rmid in rmids:
            data = lpop(rmid)
            # delete the expired rmid
            pipe.delete(rmid)
            print("Deleting", rmid)
            # MID
            mid, epoch = rmid.decode().split(":")
            # print(data)
            data['MID'] = [mid]
            # Log
            logger_queue.put({rmid: data})

        # sleep
        time.sleep(0.01)
