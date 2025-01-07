import redis

class Cache:
    def __init__(self):
        self.client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

    def get(self, key):
        return self.client.get(key)

    def set(self, key, value):
        self.client.set(key, value)