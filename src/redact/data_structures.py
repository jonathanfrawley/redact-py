from db import get_redis_conn


class RList(object):
    pass


class RHash(object):
    pass


class Set(object):
    pass


class SortedSet(object):
    def __init__(self, key):
        self.key = key

    def zadd(self, *args, **kwargs):
        return get_redis_conn().zadd(self.key, *args, **kwargs)

    def zcard(self):
        return get_redis_conn().zcard(self.key)

    def zrangebyscore(self, min, max):
        return get_redis_conn().zrangebyscore(self.key, min, max)
