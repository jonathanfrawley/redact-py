import json
import threading

from db import get_redis_conn


thread_local = threading.local()


class KeyValueField(object):
    def __init__(self, key_short, value, default_value=None):
        self.key_short = key_short
        self.value = value
        self.default_value = default_value


class BaseModel(object):
    def __init__(self, key):
        self.key = key
        self.version = KeyValueField('_v', 0)

    def save_now(self):
        pass

    def save_on_commit(self):
        pass

    def get_migrations(self):
        return []


def _get_value_dict(base_model, is_short, dump_value):
    value_dict = {}
    for k, v in base_model.__dict__.iteritems():
        if isinstance(v, KeyValueField):
            key = k
            if is_short:
                key = v.key_short
            if dump_value:
                value_dict[key] = json.dumps(v.value)
            else:
                value_dict[key] = v.value
    return value_dict


def model_load(base_model):
    model_dict = get_redis_conn().hgetall(base_model.key)
    new_dict = {}
    for k, v in base_model.__dict__.iteritems():
        new_dict[k] = v
        if isinstance(v, KeyValueField):
            if v.key_short in model_dict:
                value = json.loads(model_dict[v.key_short])
            else:
                value = new_dict[k].default_value
            new_dict[k].value = value
    base_model.__dict__ = new_dict
    for migration in base_model.get_migrations()[base_model.version.value:]:
        migration(base_model)
    base_model.version.value = len(base_model.get_migrations())


def model_save(base_model):
    value_dict = _get_value_dict(base_model, True, True)
    value_dict['_v'] = len(base_model.get_migrations())
    get_redis_conn().hmset(base_model.key, value_dict)


def model_dump(base_model):
    return json.dumps(_get_value_dict(base_model, False, False))
