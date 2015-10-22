#redact-py
Redact is a KISS ORM for python with transaction support.

[![Build Status](https://travis-ci.org/df3n5/redact-py.svg?branch=master)](https://travis-ci.org/df3n5/redact-py)

##License
MIT license, see LICENSE.

##Basic Usage
###Defining models:
```python
import redact

class Prisoner(redact.BaseModel):
	def __init__(self, key, name=None, password=None):
		super(Prisoner, self).__init__(key)
		self.name = redact.KeyValueField('n', name)
		self.password = redact.KeyValueField('p', password)
```


###Creating models:
```python
prisoner = Prisoner('num_6', "Patrick McGoohan", "iamnotanumber6")
redact.save(prisoner)
```

###Loading models:
```python
prisoner = Prisoner('num_6')
redact.load(prisoner)
print("Name : {}".format(prisoner.name))  # Prints "Name : Patrick McGoohan"
```

##Advanced usage
###Transactions:
Delays all writes and deletes until the end of the wrapped function:
```python
prisoner = Prisoner('num_1', "??", "popgoesthewheasel")
redact.save(prisoner)
prisoner = Prisoner('num_2', "Colin Gordon", "The General")
redact.save(prisoner)

@redact.transaction
def delete_number_1_and_2():
    number_1 = Prisoner('num_1')
	redact.load(number_1)
	number_2 = Prisoner('num_2')
	redact.load(number_2)
	redact.delete(number_1)  # Not actually deleted until end of function
	redact.delete(number_2)
	
delete_number_1_and_2()
```

###Data structures
####Sorted Set
```python
sorted_set = redact.SortedSet('prisoner_zset')
sorted_set.zadd("num_6", 6, "num_1", 1, "num_2", 2)
result = sorted_set.zrangebyscore(0, 5)  # Get first 5 prisoner IDs
print(result[0])  # Prints "num_1"
print(result[1])  # Prints "num_2"
print(len(result))  # Prints "2"
```

####Set
```python
set_a = redact.Set('prisoner_set_a')
set_a.add("num_1")
set_a.add("num_2")

set_b = redact.Set('prisoner_set_b')
set_b.add("num_2")
set_b.add("num_6")

set_a.difference_update(set_b)
print set_a.smembers()  # Prints "set(['num_1'])"
```

####Hashset
```python
prisoner_hash = redact.Hashset('prisoner_hashset')
prisoner_hash['num_6'] = 'uncooperative'
print 'num_6' in prisoner_hash  # Prints "True"
```

####List
```python
prisoner_list = redact.List('prisoner_list')
prisoner_list.lpush('num_1', 'num_2')
prisoner_list.rpush('num_5', 'num_6')
print prisoner_list.rpop()  # Prints "num_1"
print prisoner_list.lpop()  # Prints "num_6"
```
