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
    def __init__(self, type, args):
        self.type = type
        self.args = args


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
        self.redis_conn.delete(key)

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
        if in_transaction():
            get_thread_local().queued_writes[key] = QueuedWrite(WriteType.HMSET, (key, values))
        else:
            self.redis_conn.hmset(key, values)

    def hexists(self, key, hkey):
        self.watch_transaction(key)
        return self.redis_conn.hexists(key, hkey)

    def hget_json(self, key, hkey):
        self.watch_transaction(key)
        return json.loads(self.redis_conn.hget(key, hkey))

    def hset_json(self, key, hkey, value):
        self.redis_conn.hset(key, hkey, json.dumps(value))

    def set(self, key, value):
        if in_transaction():
            get_thread_local().queued_writes[key] = QueuedWrite(WriteType.SET, (key, value))
        else:
            self.redis_conn.set(key, value)

    def setex(self, key, value, timeout):
        if in_transaction():
            get_thread_local().queued_writes[key] = QueuedWrite(WriteType.SETEX, (key, timeout, value))
        else:
            self.redis_conn.setex(key, timeout, value)

    def save_json(self, key, obj):
        if in_transaction():
            get_thread_local().queued_writes[key] = QueuedWrite(WriteType.SET, (key, json.dumps(obj)))
        else:
            self.redis_conn.set(key, json.dumps(obj))


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
