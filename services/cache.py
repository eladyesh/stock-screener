import time

_cache = {
    "data": None,
    "timestamp": 0
}

TTL = 60  # seconds

def set_cache(data):
    _cache["data"] = data
    _cache["timestamp"] = time.time()

def get_cache():
    if _cache["data"] and (time.time() - _cache["timestamp"] < TTL):
        return _cache["data"]
    return None