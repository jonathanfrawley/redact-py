class NoSuchDbError(Exception):
    pass


class MaxTransactionRetriesError(Exception):
    pass


class UnknownQueuedWriteTypeError(Exception):
    pass
