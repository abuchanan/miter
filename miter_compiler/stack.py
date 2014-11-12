class Stack(object):

    def __init__(self, factory=list):
        self._factory = factory
        self._data = []
        self.save()

    @property
    def level(self):
        return len(self._data) - 1

    @property
    def top(self):
        return self._data[-1]

    def save(self):
        self._data.append(self._factory())

    def restore(self):
        if self.level == 0:
            raise Exception("Already at level 0")

        return self._data.pop()
