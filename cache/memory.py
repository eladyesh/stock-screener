import time

CACHE = {}
TTL = 300  # 5 minutes


def get_cache(key):
    if key in CACHE:
        data, timestamp = CACHE[key]

        if time.time() - timestamp < TTL:
            return data

    return None


def set_cache(key, value):
    CACHE[key] = (value, time.time())