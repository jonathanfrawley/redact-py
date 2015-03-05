import json

from redact.model import model_dump
from redact.model import model_load
from redact.model import model_save
from redact.db import get_redis_conn

from fixtures import model
from fixtures import saved_model
from fixtures import TestModel
from fixtures import TestMigratedModel
from fixtures import TestRemoteModel


### Tests
def test_model_load(saved_model):
    assert len(get_redis_conn().keys(saved_model.key)) == 1
    loaded_model = TestModel('test_model_1')
    model_load(loaded_model)
    assert loaded_model.test_str_1.v == saved_model.test_str_1.v
    assert loaded_model.test_str_2.v == saved_model.test_str_2.v
    assert loaded_model.test_str_3.v == saved_model.test_str_3.v


def test_model_save(model):
    assert len(get_redis_conn().keys(model.key)) == 0
    model_save(model)
    assert len(get_redis_conn().keys(model.key)) == 1
    db_model = get_redis_conn().hgetall(model.key)
    assert db_model is not None
    assert model.test_str_1.v == json.loads(db_model['t1'])
    assert model.test_str_2.v == json.loads(db_model['t2'])
    assert model.test_str_3.v == json.loads(db_model['t3'])


def test_model_dump(model):
    json_model = model_dump(model)
    reloaded_json = json.loads(json_model)
    assert model.test_str_1.v == reloaded_json['test_str_1']
    assert model.test_str_2.v == reloaded_json['test_str_2']
    assert model.test_str_3.v == reloaded_json['test_str_3']


def test_model_migration(saved_model):
    assert saved_model.version.v == 0
    loaded_model = TestMigratedModel('test_model_1')
    model_load(loaded_model)
    assert loaded_model.test_str_1.v == saved_model.test_str_1.v
    assert loaded_model.test_str_2.v == saved_model.test_str_2.v
    assert loaded_model.test_str_3.v == saved_model.test_str_3.v
    assert loaded_model.test_extra_value_1.v == "TEST_MIGRATION_VALUE_1"
    assert loaded_model.test_extra_value_2.v == "TEST_MIGRATION_VALUE_2"
    assert loaded_model.version.v == 2

    # Verify migration doesn't happen next time
    loaded_model.test_extra_value_1.v = 'different value 1'
    loaded_model.test_extra_value_2.v = 'different value 2'
    model_save(loaded_model)
    new_loaded_model = TestMigratedModel('test_model_1')
    model_load(new_loaded_model)
    assert new_loaded_model.test_extra_value_1.v != "TEST_MIGRATION_VALUE_1"
    assert new_loaded_model.test_extra_value_2.v != "TEST_MIGRATION_VALUE_2"
    assert new_loaded_model.test_extra_value_1.v == loaded_model.test_extra_value_1.v
    assert new_loaded_model.test_extra_value_2.v == loaded_model.test_extra_value_2.v
    assert new_loaded_model.version.v == 2


def test_model_remote_key_value(saved_model):
    loaded_model = TestModel('test_model_1')
    model_load(loaded_model)
    loaded_remote_model = TestRemoteModel(loaded_model.test_remote_key_value.k)
    model_load(loaded_remote_model)
    assert loaded_remote_model.test_str_1.v == 'd'
