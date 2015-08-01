import json

from redact import delete
from redact.db import get_redis_conn
from redact.model import load
from redact.model import save
from redact.transaction import transaction

from fixtures import saved_list_model
from fixtures import saved_model
from fixtures import TestListModel
from fixtures import TestModel


@transaction
def simple_transaction_fn():
    loaded_model = TestModel('test_model_1')
    load(loaded_model)
    loaded_model.test_str_1 = "blah blah"
    save(loaded_model)


@transaction
def delete_in_transaction_fn():
    loaded_model = TestModel('test_model_1')
    load(loaded_model)
    loaded_list_model = TestListModel('test_list_model_1')
    load(loaded_list_model)
    loaded_list_model.l.remove(loaded_model.key)
    delete(loaded_model)
    save(loaded_list_model)


def test_simple_transaction(saved_model):
    simple_transaction_fn()
    db_model = get_redis_conn().hgetall(saved_model.key)
    assert db_model is not None
    assert "blah blah" == json.loads(db_model['t1'])


def test_delete_in_transaction(saved_model, saved_list_model):
    t = TestListModel(saved_list_model.key)
    load(t)
    t.l.append(saved_model.key)
    save(t)
    t = TestListModel(saved_list_model.key)
    load(t)
    assert len(t.l) == 1
    delete_in_transaction_fn()
    db_model = get_redis_conn().hgetall(saved_model.key)
    assert len(db_model.keys()) == 0
    saved_list_db_model = get_redis_conn().hgetall(saved_list_model.key)
    assert len(json.loads(saved_list_db_model['l'])) == 0
