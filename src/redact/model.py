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


def _get_value_dict(base_model, is_short):
    value_dict = {}
    for k, v in base_model.__dict__.iteritems():
        if isinstance(v, KeyValueField):
            if is_short:
                value_dict[v.key_short] = json.dumps(v.value)
            else:
                value_dict[k] = json.dumps(v.value)
    return value_dict


def hashset_save(base_model):
    get_redis_conn().hmset(base_model.key, _get_value_dict(base_model, True))


def json_dump(base_model):
    return json.dumps(_get_value_dict(base_model, False))
