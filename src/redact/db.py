import json
import redis
import threading


thread_local = threading.local()


class DbTypes:
    REDIS = 0


class RedisConn:
    def __init__(self, host="localhost", port=6379, db_num=0):
        self.redis_conn =  redis.Redis(host=host, port=port, db=db_num)

    def close(self):
        self.redis_conn.close()

    def delete(self, key):
        self.redis_conn.delete(key)

    def load_json(self, key):
        obj = self.redis_conn.get(key)
        if obj is None:
            return None
        else:
            return json.loads(obj)

    def get(self, key):
        return self.redis_conn.get(key)

    def keys(self, pattern):
        return self.redis_conn.keys(pattern)

    def hkeys(self, key):
        return self.redis_conn.hkeys(key)

    def hgetall(self, key):
        return self.redis_conn.hgetall(key)

    def hmget(self, key, hkeys):
        return self.redis_conn.hmget(key, hkeys)

    def hmget_json(self, key, hkeys):
        values = self.redis_conn.hmget(key, hkeys)
        result = []
        for value in values:
            result.append(json.loads(value))
        return result

    def hmset(self, key, values):
        self.redis_conn.hmset(key, values)

    def hexists(self, key, hkey):
        return self.redis_conn.hexists(key, hkey)

    def hget_json(self, key, hkey):
        return json.loads(self.redis_conn.hget(key, hkey))

    def hset_json(self, key, hkey, value):
        self.redis_conn.hset(key, hkey, json.dumps(value))

    def set(self, key, value):
        self.redis_conn.set(key, value)

    def setex(self, key, value, timeout):
        self.redis_conn.setex(key, timeout, value)

    def save_json(self, key, obj):
        self.redis_conn.set(key, json.dumps(obj))


# Errors
class NoSuchDbError(Exception):
    pass


def get_new_conn(db_type):
    if db_type == DbTypes.REDIS:
        return RedisConn()
    else:
        raise NoSuchDbError("Db type <{}> is not supported".format(db_type))


def get_redis_conn():
    try:
        return thread_local.redis_conn
    except Exception:
        thread_local.redis_conn = get_new_conn(DbTypes.REDIS)
        return thread_local.redis_conn
