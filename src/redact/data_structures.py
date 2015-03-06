from collections import Sequence

from db import get_redis_conn


class List(Sequence):
    def __init__(self, key):
        self.key = key

    def __len__(self):
        return get_redis_conn().llen(self.key)

    def __getitem__(self, slice):
        return self.lrange(0, -1)[slice]

    def lindex(self, idx):
        return get_redis_conn().lindex(self.key, idx)

    def lpush(self, *args):
        return get_redis_conn().lpush(self.key, *args)

    def rpush(self, *args):
        return get_redis_conn().rpush(self.key, *args)

    def lrange(self, start, end):
        return get_redis_conn().lrange(self.key, start, end)

    def lpop(self):
        return get_redis_conn().lpop(self.key)

    def rpop(self):
        return get_redis_conn().rpop(self.key)


class RHash(object):
    pass


class Set(object):
    pass


class SortedSet(object):
    def __init__(self, key):
        self.key = key

    def zadd(self, *args, **kwargs):
        get_redis_conn().zadd(self.key, *args, **kwargs)

    def zcard(self):
        return get_redis_conn().zcard(self.key)

    def zrangebyscore(self, min, max):
        return get_redis_conn().zrangebyscore(self.key, min, max)

    def zremrangebyscore(self, min, max):
        return get_redis_conn().zremrangebyscore(self.key, min, max)
