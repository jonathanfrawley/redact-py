import json

from db import get_redis_conn


class KeyValueField(object):
    def __init__(self, key_short, value=None):
        self.key_short = key_short
        self.value = value


class BaseModel(object):
    def __init__(self, key):
        self.key = key

    def save_now(self):
        pass

    def save_on_commit(self):
        pass


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
            new_dict[k].value = json.loads(model_dict[v.key_short])
    base_model.__dict__ = new_dict
    return base_model


def model_save(base_model):
    get_redis_conn().hmset(base_model.key, _get_value_dict(base_model, True, True))


def model_dump(base_model):
    return json.dumps(_get_value_dict(base_model, False, False))
