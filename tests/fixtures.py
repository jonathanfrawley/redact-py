import pytest

from redact.data_structures import List
from redact.data_structures import SortedSet
from redact.db import get_redis_conn
from redact.model import BaseModel
from redact.model import KeyValueField
from redact.model import model_save
from redact.model import RemoteKeyValueField


class TestModel(BaseModel):
    def __init__(self, key, test_str_value_1=None, test_str_value_2=None, test_str_value_3=None):
        super(TestModel, self).__init__(key)
        self.test_str_1 = KeyValueField('t1', test_str_value_1)
        self.test_str_2 = KeyValueField('t2', test_str_value_2)
        self.test_str_3 = KeyValueField('t3', test_str_value_3)
        self.test_remote_key_value = RemoteKeyValueField('tr', 'trkv:{}'.format(key))


class TestMigratedModel(BaseModel):
    def __init__(self, key, test_str_value_1=None, test_str_value_2=None, test_str_value_3=None, test_extra_value_1=None, test_extra_value_2=None):
        super(TestMigratedModel, self).__init__(key)
        self.test_str_1 = KeyValueField('t1', test_str_value_1)
        self.test_str_2 = KeyValueField('t2', test_str_value_2)
        self.test_str_3 = KeyValueField('t3', test_str_value_3)
        self.test_extra_value_1 = KeyValueField('e1', test_extra_value_1)
        self.test_extra_value_2 = KeyValueField('e2', test_extra_value_2)

    def get_migrations(self):
        def migration_1(base_model):
            base_model.test_extra_value_1.value = "TEST_MIGRATION_VALUE_1"

        def migration_2(base_model):
            base_model.test_extra_value_2.value = "TEST_MIGRATION_VALUE_2"
        return [migration_1, migration_2]


class TestRemoteModel(BaseModel):
    def __init__(self, key, test_str_value_1=None):
        super(TestRemoteModel, self).__init__(key)
        self.test_str_1 = KeyValueField('t1', test_str_value_1)


### Test fixtures
@pytest.fixture
def model(request):
    model = TestModel('test_model_1', 'a', 'b', 'c')

    def fin():
        get_redis_conn().delete(model.key)
    request.addfinalizer(fin)
    return model


@pytest.fixture
def saved_model(request):
    model = TestModel('test_model_1', 'a', 'b', 'c')
    remote_model = TestRemoteModel(model.test_remote_key_value.remote_key, 'd')
    model_save(model)
    model_save(remote_model)

    def fin():
        get_redis_conn().delete(model.key)
        get_redis_conn().delete(remote_model.key)
    request.addfinalizer(fin)
    return model


@pytest.fixture
def sorted_set(request):
    model = SortedSet('test_sorted_set')

    def fin():
        get_redis_conn().delete('test_sorted_set')
    request.addfinalizer(fin)
    return model


@pytest.fixture
def list(request):
    model = List('test_list')

    def fin():
        get_redis_conn().delete('test_list')
    request.addfinalizer(fin)
    return model
