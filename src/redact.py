
class KeyValueField(object):
    def __init__(self, key_short, key_long):
        self.key_short = key_short
        self.key_long = key_long
        self.value = None


class BaseModel(object):
    def __init__(self, key):
        self.key = key

    def save_now(self):
        pass

    def save_on_commit(self):
        pass


def hashset_save(base_model):
    for var in vars(base_model):
        if isinstance(var, KeyValueField):
            k = var.self.key_short
            v = base_model.key
            if isinstance(v, BaseModel):
                value_json = hashset_save(v)
            else:
                value_json = v
            get_conn().hset(base_model.key, k, value_json)
            return KeyValueField
