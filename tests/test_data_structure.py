from redact.data_structures import SortedSet


def test_sorted_set_add():
    sorted_set = SortedSet('test_sorted_set')
    sorted_set.zadd('test1', 100, 'test2', 200)
    assert 2 == sorted_set.zcard()


def test_sorted_set_score():
    sorted_set = SortedSet('test_sorted_set')
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


def test_sorted_set_rem():
    sorted_set = SortedSet('test_sorted_set')
    sorted_set.zadd('test1', 100, 'test2', 200)
    assert sorted_set.zcard() == 2
    sorted_set.zremrangebyscore(0, 300)
    assert sorted_set.zcard() == 0
