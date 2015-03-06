from redact.data_structures import List
from redact.data_structures import SortedSet

from fixtures import list
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
