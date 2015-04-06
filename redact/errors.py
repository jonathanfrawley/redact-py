class NoSuchDbError(Exception):
    pass


class NoSuchKeyError(Exception):
    pass


class MaxTransactionRetriesError(Exception):
    pass


class UnkownQueuedWriteFuncError(Exception):
    pass
