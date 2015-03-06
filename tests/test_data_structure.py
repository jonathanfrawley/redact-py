import pytest

from redact.data_structures import List
from redact.data_structures import SortedSet

from fixtures import hashset
from fixtures import list
from fixtures import set
from fixtures import set_2
from fixtures import sorted_set


# Sorted sets
def test_sorted_set_add(sorted_set):
    sorted_set.zadd('test1', 100, 'test2', 200)
    assert 2 == sorted_set.zcard()


def test_sorted_set_score(sorted_set):
    sorted_set.zadd('test1', 100, 'test2', 200)
    result = sorted_set.zrangebyscore(0, 150)
    assert 1 == len(result)
    assert 'test1' == result[0]
    result = sorted_set.zrangebyscore(150, 250)
    assert 1 == len(result)
    assert 'test2' == result[0]
    result = sorted_set.zrangebyscore('-inf', '+inf')
    assert 2 == len(result)
    assert 'test1' == result[0]
    assert 'test2' == result[1]


def test_sorted_set_rem(sorted_set):
    sorted_set.zadd('test1', 100, 'test2', 200)
    assert sorted_set.zcard() == 2
    sorted_set.zremrangebyscore(0, 300)
    assert sorted_set.zcard() == 0


# Lists
def test_list_push(list):
    list.rpush('blah1', 'blah2')
    assert len(list) == 2
    list.lpush('blah0')
    assert len(list) == 3
    assert list[0] == 'blah0'


def test_list_read(list):
    list.rpush('blah1', 'blah2', 'blah3')
    all_elems = list.lrange(0, -1)
    assert all_elems == ['blah1', 'blah2', 'blah3']
    assert list[1] == 'blah2'
    assert list.lindex(2) == 'blah3'
    right_elem = list.rpop()
    assert len(list) == 2
    assert right_elem == 'blah3'
    left_elem = list.lpop()
    assert len(list) == 1
    assert left_elem == 'blah1'
    left_elem = list.lpop()
    assert len(list) == 0
    assert left_elem == 'blah2'


def test_list_del(list):
    list.rpush('blah1', 'blah2', 'blah3')
    assert len(list) == 3
    list.ltrim(0, 1)
    assert len(list) == 2
    list.ltrim(0, 0)
    assert len(list) == 1


# Hashset
def test_hashset_add(hashset):
    hashset['a'] = 'test1'
    hashset['b'] = 'test2'
    hashset['c'] = 'test3'
    assert len(hashset.keys()) == 3
    assert sorted(hashset.keys()) == ['a', 'b', 'c']
    assert len(hashset.values()) == 3
    assert sorted(hashset.values()) == ['test1', 'test2', 'test3']


def test_hashset_read(hashset):
    hashset['a'] = 'test1'
    hashset['b'] = 'test2'
    hashset['c'] = 'test3'
    assert hashset['a'] == 'test1'
    assert hashset['b'] == 'test2'
    assert hashset['c'] == 'test3'


def test_hashset_del(hashset):
    hashset['a'] = 'test1'
    hashset['b'] = 'test2'
    hashset['c'] = 'test3'
    del hashset['a']
    assert len(hashset.keys()) == 2
    with pytest.raises(KeyError):
        print("Should raise an exception: {}".format(hashset['a']))


# Set
def test_set_add(set, set_2):
    set.add("test1")
    assert len(set) == 1
    set.add("test2")
    assert len(set) == 2
    set_2.add("test3")
    set.update(set_2)
    assert len(set) == 3


def test_set_intersection(set, set_2):
    set.add("test1")
    set.add("test2")
    set_2.add("test2")
    set.intersection_update(set_2)
    assert len(set) == 1
    assert "test2" in set


def test_set_difference(set, set_2):
    set.add("test1")
    set.add("test2")
    set_2.add("test2")
    set.difference_update(set_2)
    assert len(set) == 1
    assert "test1" in set


def test_set_read(set):
    set.add("test1")
    set.add("test2")
    assert len(set) == 2
    assert "test1" in set
    assert "test2" in set


def test_set_del(set):
    set.add("test1")
    set.add("test2")
    assert len(set) == 2
    set.remove("test2")
    assert len(set) == 1
    with pytest.raises(KeyError):
        set.remove("test2")
    set.discard("test2")
    assert len(set) == 1
    set.discard("test1")
    assert len(set) == 0
    set.add("test1")
    set.add("test2")
    set.pop()
    assert len(set) == 1
    set.clear()
    assert len(set) == 0
