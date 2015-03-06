import collections

from db import get_redis_conn


class List(collections.Sequence):
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

    def ltrim(self, start, end):
        return get_redis_conn().ltrim(self.key, start, end)


class Hashset(collections.MutableMapping):
    def __init__(self, key):
        self.key = key

    def __getitem__(self, slice):
        return self.hgetall()[slice]

    def __setitem__(self, key, value):
        return self.hset(key, value)

    def __delitem__(self, key):
        return self.hdel(key)

    def __iter__(self):
        return iter(self.hgetall())

    def __len__(self):
        return self.hlen()

    def hgetall(self):
        return get_redis_conn().hgetall(self.key)

    def hset(self, key, value):
        return get_redis_conn().hset(self.key, key, value)

    def hlen(self):
        return get_redis_conn().hlen(self.key)

    def hdel(self, *args):
        return get_redis_conn().hdel(self.key, *args)


class Set(collections.MutableSet):
    def __init__(self, key):
        self.key = key

    def __contains__(self, elem):
        return self.sismember(elem)

    def __iter__(self):
        return iter(self.smembers())

    def __len__(self):
        return self.scard()

    def update(self, other_set):
        return self.sunionstore(other_set.key)

    def intersection_update(self, other_set):
        return self.sinterstore(other_set.key)

    def difference_update(self, other_set):
        return self.sdiffstore(other_set.key)

    def add(self, elem):
        return self.sadd(elem)

    def discard(self, elem):
        return self.srem(elem)

    def sismember(self, elem):
        return get_redis_conn().sismember(self.key, elem)

    def smembers(self):
        return get_redis_conn().smembers(self.key)

    def scard(self):
        return get_redis_conn().scard(self.key)

    def sadd(self, elem):
        return get_redis_conn().sadd(self.key, elem)

    def srem(self, elem):
        return get_redis_conn().srem(self.key, elem)

    def sunionstore(self, other_set_key):
        return get_redis_conn().sunionstore(self.key, other_set_key)

    def sinterstore(self, other_set_key):
        return get_redis_conn().sinterstore(self.key, other_set_key)

    def sunion(self, other_set_key):
        return get_redis_conn().sunion(self.key, other_set_key)

    def sinter(self, other_set_key):
        return get_redis_conn().sinter(self.key, other_set_key)

    def sdiffstore(self, other_set_key):
        return get_redis_conn().sdiffstore(self.key, other_set_key)

    def sdiff(self, other_set_key):
        return get_redis_conn().sdiff(self.key, other_set_key)


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
