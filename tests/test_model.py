import json
import pytest

from redact.model import BaseModel
from redact.model import hashset_save
from redact.model import KeyValueField
from redact.db import get_redis_conn


class TestModel(BaseModel):
    def __init__(self, key, test_str_value_1, test_str_value_2, test_str_value_3):
        super(TestModel, self).__init__(key)
        self.test_str_1 = KeyValueField('t1', test_str_value_1)
        self.test_str_2 = KeyValueField('t2', test_str_value_2)
        self.test_str_3 = KeyValueField('t3', test_str_value_3)


### Test fixtures
@pytest.fixture
def model(request):
    model = TestModel('test_model_1', 'a', 'b', 'c')

    def fin():
        get_redis_conn().delete(model.key)
    request.addfinalizer(fin)
    return model


### Hashset save test
def test_hashset_save(model):
    assert len(get_redis_conn().keys(model.key)) == 0
    hashset_save(model)
    assert len(get_redis_conn().keys(model.key)) == 1
    db_model = get_redis_conn().hgetall(model.key)
    assert db_model is not None
    assert model.test_str_1.value == json.loads(db_model['t1'])
    assert model.test_str_2.value == json.loads(db_model['t2'])
    assert model.test_str_3.value == json.loads(db_model['t3'])
