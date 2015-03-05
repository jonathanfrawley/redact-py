import json

from redact.db import get_redis_conn
from redact.model import model_load
from redact.model import model_save
from redact.transaction import transaction

from fixtures import saved_model
from fixtures import TestModel


@transaction
def simple_transaction_fn():
    loaded_model = TestModel('test_model_1')
    model_load(loaded_model)
    loaded_model.test_str_1.v = "blah blah"
    model_save(loaded_model)


def test_simple_transaction(saved_model):
    simple_transaction_fn()
    db_model = get_redis_conn().hgetall(saved_model.key)
    assert db_model is not None
    assert "blah blah" == json.loads(db_model['t1'])
