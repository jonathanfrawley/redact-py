import json

from db import get_redis_conn
from errors import NoSuchKeyError


class KeyValueField(object):
    def __init__(self, key_short, value, default_value=None):
        self.key_short = key_short
        self.value = value
        self.default_value = default_value

    @property
    def v(self):
        return self.value

    @v.setter
    def v(self, value):
        self.value = value


class RemoteKeyValueField(object):
    def __init__(self, key_short, remote_key, default_remote_key=None):
        self.key_short = key_short
        self.remote_key = remote_key
        self.default_remote_key = default_remote_key

    @property
    def k(self):
        return self.remote_key

    @k.setter
    def k(self, value):
        self.remote_key = value


class BaseModel(object):
    def __init__(self, key):
        self.key = key
        self.version = KeyValueField('_v', 0)

    def get_migrations(self):
        return []

    def __getattribute__(self, name):
        v = object.__getattribute__(self, name)
        if isinstance(v, KeyValueField):
            return v.v
        if isinstance(v, RemoteKeyValueField):
            return v.k
        else:
            return v

    def __setattr__(self, name, value):
        if hasattr(self, name):
            v = object.__getattribute__(self, name)
            if isinstance(v, KeyValueField):
                v.v = value
                return
        return object.__setattr__(self, name, value)


def _get_key(k, v, is_short):
    key = k
    if is_short:
        key = v.key_short
    return key


def _get_value_dict(base_model, is_short, dump_value):
    value_dict = {}
    for k, v in base_model.__dict__.iteritems():
        if isinstance(v, KeyValueField):
            key = _get_key(k, v, is_short)
            if dump_value:
                value_dict[key] = json.dumps(v.value)
            else:
                value_dict[key] = v.value
        if isinstance(v, RemoteKeyValueField):
            key = _get_key(k, v, is_short)
            if dump_value:
                value_dict[key] = json.dumps(v.remote_key)
            else:
                value_dict[key] = v.remote_key
    return value_dict


def load_from_dict(base_model, model_dict):
    new_dict = {}
    for k, v in base_model.__dict__.iteritems():
        new_dict[k] = v
        if isinstance(v, KeyValueField):
            if k in model_dict:
                value = model_dict[k]
            else:
                value = new_dict[k].default_value
            new_dict[k].value = value
        elif isinstance(v, RemoteKeyValueField):
            if k in model_dict:
                remote_key = model_dict[k]
            else:
                remote_key = new_dict[k].default_remote_key
            new_dict[k].remote_key = remote_key
    base_model.__dict__ = new_dict


def load(base_model):
    model_dict = get_redis_conn().hgetall(base_model.key)
    if not model_dict:
        raise NoSuchKeyError("Key {} does not exist in DB.".format(base_model.key))
    new_dict = {}
    for k, v in base_model.__dict__.iteritems():
        new_dict[k] = v
        if isinstance(v, KeyValueField):
            if v.key_short in model_dict:
                value = json.loads(model_dict[v.key_short])
            else:
                value = new_dict[k].default_value
            new_dict[k].value = value
        elif isinstance(v, RemoteKeyValueField):
            if v.key_short in model_dict:
                remote_key = json.loads(model_dict[v.key_short])
            else:
                remote_key = new_dict[k].default_remote_key
            new_dict[k].remote_key = remote_key
    base_model.__dict__ = new_dict
    for migration in base_model.get_migrations()[base_model.version:]:
        migration(base_model)
    base_model.version = len(base_model.get_migrations())


def save(base_model):
    value_dict = _get_value_dict(base_model, True, True)
    value_dict['_v'] = len(base_model.get_migrations())
    get_redis_conn().hmset(base_model.key, value_dict)


def dump(base_model):
    return json.dumps(_get_value_dict(base_model, False, False))


def delete(base_model):
    return get_redis_conn().delete(base_model.key)


def get_dict(base_model):
    return _get_value_dict(base_model, False, False)
