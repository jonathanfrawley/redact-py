import collections

from db import WriteType
from db import get_thread_local
from functools import wraps
from redis.exceptions import WatchError

from db import get_redis_conn
from errors import MaxTransactionRetriesError
from errors import UnkownQueuedWriteFuncError


MAX_TRANSACTION_RETRIES = 500


def execute_queued_write(pipe, queued_write):
    func = getattr(pipe, queued_write.func_name)
    if func is not None:
        func(*queued_write.args, **queued_write.kwargs)
    else:
        raise UnkownQueuedWriteFuncError("{} is an unknown queued write func".format(queued_write.func))


def transaction(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        with get_redis_conn().pipeline() as pipe:
            get_thread_local().transaction_pipeline = pipe
            get_thread_local().in_transaction = True
            for i in xrange(MAX_TRANSACTION_RETRIES):
                get_thread_local().queued_writes = collections.defaultdict(list)
                try:
                    ret_value = f(*args, **kwargs)
                    pipe.multi()
                    for queued_write_list in get_thread_local().queued_writes.values():
                        for queued_write in queued_write_list:
                            execute_queued_write(pipe, queued_write)
                    pipe.execute()
                    get_thread_local().in_transaction = False
                    return ret_value
                except WatchError:
                    continue
                except Exception:
                    get_thread_local().in_transaction = False
                    raise
            get_thread_local().in_transaction = False
            raise MaxTransactionRetriesError("Maximum retries done on transaction, bailing out.")
    return wrapper
