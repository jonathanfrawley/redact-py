import redact


class Prisoner(redact.BaseModel):
    def __init__(self, key, name=None, password=None):
        super(Prisoner, self).__init__(key)
        self.name = redact.KeyValueField('n', name)
        self.password = redact.KeyValueField('p', password)

i = 0


def save_model():
    global i
    prisoner = Prisoner('num_{}'.format(i), "Patrick McGoohan", "iamnotanumber6")
    redact.save(prisoner)
    i += 1


def delete_model():
    global i
    prisoner = Prisoner('num_{}'.format(i))
    redact.delete(prisoner)
    i += 1


def read_model():
    global i
    prisoner = Prisoner('num_{}'.format(i), "Patrick McGoohan", "iamnotanumber6")
    redact.load(prisoner)
    i += 1

def update_model():
    global i
    prisoner = Prisoner('num_{}'.format(i), "Patrick McGoohan", "iamnotanumber6")
    redact.load(prisoner)
    i += 1
    redact.save(prisoner)


if __name__ == '__main__':
    global i
    import timeit
    n_writes = 10000
    write_time = timeit.timeit("save_model()", setup="from __main__ import save_model", number=n_writes)
    print("{} writes completed in {} seconds".format(n_writes, write_time))

    i = 0
    read_time = timeit.timeit("read_model()", setup="from __main__ import read_model", number=n_writes)
    print("{} reads completed in {} seconds".format(n_writes, read_time))

    i = 0
    update_time = timeit.timeit("update_model()", setup="from __main__ import update_model", number=n_writes)
    print("{} updates completed in {} seconds".format(n_writes, update_time))

    i = 0
    delete_time = timeit.timeit("delete_model()", setup="from __main__ import delete_model", number=n_writes)
    print("{} deletes completed in {} seconds".format(n_writes, delete_time))
