import json
import redis
import threading
import errors


thread_local = threading.local()


class DbTypes:
    REDIS = 0


class WriteType:
    SET = 0
    SETEX = 1
    HSET = 2
    HMSET = 3


class QueuedWrite:
    def __init__(self, func_name, args, kwargs):
        self.func_name = func_name
        self.args = args
        self.kwargs = kwargs


def in_transaction():
    return getattr(get_thread_local(), 'in_transaction', False)


def get_thread_local():
    return thread_local


class RedisConn:
    def __init__(self, host="localhost", port=6379, db_num=0):
        self.redis_conn_obj = redis.Redis(host=host, port=port, db=db_num)

    def close(self):
        self.redis_conn.close()

    def delete(self, key):
        self.do_write('delete', (key), ())

    @property
    def redis_conn(self):
        if in_transaction():
            return get_thread_local().transaction_pipeline
        else:
            return self.redis_conn_obj

    def load_json(self, key):
        obj = self.redis_conn.get(key)
        if obj is None:
            return None
        else:
            return json.loads(obj)

    def watch_transaction(self, key):
        if in_transaction():
            get_thread_local().transaction_pipeline.watch(key)

    def pipeline(self):
        return self.redis_conn.pipeline()

    def get(self, key):
        self.watch_transaction(key)
        return self.redis_conn.get(key)

    def keys(self, pattern):
        return self.redis_conn.keys(pattern)

    def set(self, key, value):
        return self.do_write('set', key, (value,))

    def setex(self, key, value, timeout):
        return self.do_write('setex', key, (value, timeout))

    def save_json(self, key, obj):
        return self.do_write('set', key, (json.dumps(obj),))

    def do_write(self, func_name, key, args, kwargs={}):
        args = (key,) + args
        if in_transaction():
            get_thread_local().queued_writes[key].append(QueuedWrite(func_name, args, kwargs))
            return None
        else:
            func = getattr(self.redis_conn, func_name)
            if func is not None:
                return func(*args, **kwargs)
            else:
                return None

    # Sorted sets
    def zadd(self, name, *args, **kwargs):
        return self.do_write('zadd', name, args, kwargs)

    def zrangebyscore(self, name, min, max):
        self.watch_transaction(name)
        return self.redis_conn.zrangebyscore(name, min, max)

    def zremrangebyscore(self, name, min, max):
        self.watch_transaction(name)
        return self.redis_conn.zremrangebyscore(name, min, max)

    def zcard(self, name):
        self.watch_transaction(name)
        return self.redis_conn.zcard(name)

    # Lists
    def llen(self, name):
        self.watch_transaction(name)
        return self.redis_conn.llen(name)

    def lindex(self, name, idx):
        self.watch_transaction(name)
        return self.redis_conn.lindex(name, idx)

    def lpush(self, name, *args):
        return self.do_write('lpush', name, args)

    def rpush(self, name, *args):
        return self.do_write('rpush', name, args)

    def lpop(self, name):
        return self.do_write('lpop', name, ())

    def rpop(self, name):
        return self.do_write('rpop', name, ())

    def lrange(self, name, start, end):
        self.watch_transaction(name)
        return self.redis_conn.lrange(name, start, end)

    def ltrim(self, name, start, end):
        return self.do_write('ltrim', name, (start, end))

    # Hashsets
    def hkeys(self, key):
        self.watch_transaction(key)
        return self.redis_conn.hkeys(key)

    def hgetall(self, key):
        self.watch_transaction(key)
        return self.redis_conn.hgetall(key)

    def hmget(self, key, hkeys):
        self.watch_transaction(key)
        return self.redis_conn.hmget(key, hkeys)

    def hmget_json(self, key, hkeys):
        self.watch_transaction(key)
        values = self.redis_conn.hmget(key, hkeys)
        result = []
        for value in values:
            result.append(json.loads(value))
        return result

    def hmset(self, key, values):
        return self.do_write('hmset', key, (values,))

    def hexists(self, key, hkey):
        self.watch_transaction(key)
        return self.redis_conn.hexists(key, hkey)

    def hget_json(self, key, hkey):
        self.watch_transaction(key)
        return json.loads(self.redis_conn.hget(key, hkey))

    def hset(self, key, hkey, value):
        return self.do_write('hset', key, (hkey, value))

    def hset_json(self, key, hkey, value):
        return self.do_write('hset', key, (hkey, json.dumps(value)))

    def hlen(self, key):
        self.watch_transaction(key)
        return self.redis_conn.hlen(key)

    def hdel(self, key, *args):
        return self.do_write('hdel', key, args)

    # Set
    def sismember(self, key, elem):
        self.watch_transaction(key)
        return self.redis_conn.sismember(key, elem)

    def smembers(self, key):
        self.watch_transaction(key)
        return self.redis_conn.smembers(key)

    def scard(self, key):
        self.watch_transaction(key)
        return self.redis_conn.scard(key)

    def sadd(self, key, elem):
        return self.do_write('sadd', key, (elem,))

    def srem(self, key, elem):
        return self.do_write('srem', key, (elem,))

    def sinter(self, set_a_key, set_b_key):
        self.watch_transaction(set_a_key)
        self.watch_transaction(set_b_key)
        return self.redis_conn.sinter(set_a_key, set_b_key)

    def sunion(self, set_a_key, set_b_key):
        self.watch_transaction(set_a_key)
        self.watch_transaction(set_b_key)
        return self.redis_conn.sunion(set_a_key, set_b_key)

    def sinterstore(self, set_a_key, set_b_key):
        return self.do_write('sinterstore', set_a_key, (set_a_key, set_b_key,))

    def sunionstore(self, set_a_key, set_b_key):
        return self.do_write('sunionstore', set_a_key, (set_a_key, set_b_key,))

    def sdiff(self, set_a_key, set_b_key):
        self.watch_transaction(set_a_key)
        self.watch_transaction(set_b_key)
        return self.redis_conn.sdiff(set_a_key, set_b_key)

    def sdiffstore(self, set_a_key, set_b_key):
        return self.do_write('sdiffstore', set_a_key, (set_a_key, set_b_key,))


# Errors
def get_new_conn(db_type):
    if db_type == DbTypes.REDIS:
        return RedisConn()
    else:
        raise errors.NoSuchDbError("Db type <{}> is not supported".format(db_type))


def get_redis_conn():
    try:
        return get_thread_local().redis_conn
    except Exception:
        get_thread_local().redis_conn = get_new_conn(DbTypes.REDIS)
        return get_thread_local().redis_conn
