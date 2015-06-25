from queue import Queue
from singleton import Singleton

class EventManager(object, metaclass=Singleton):

    def __init__(self):
        self._events = {}
        self._queue = Queue()

    def emit(self, name, args=None):
        self._queue((name, args))

    def update(self):
        while not self._queue.empty():
            name, event = self._queue.get_nowait()
            if not name in self._events:
                return

            for cb in self._events[name]:
                cb(event)

    def register(self, name, cb):
        if not name in self._events:
            self._events[name] = []

        self._events[name].append(cb)
        print('Registering event: %s -%s' %(name,cb))
