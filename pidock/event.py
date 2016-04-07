"""Export an EventManager Singleton."""

from queue import Queue
from .singleton import Singleton


class EventManager(object, metaclass=Singleton):
    """Singleton class for event handling."""

    def __init__(self):
        """Constructor."""
        self._events = {}
        self._queue = Queue()

    def emit(self, name, args=None):
        """Queue event for processing."""
        self._queue.put((name, args))

    def update(self):
        """Process queue until empty."""
        while not self._queue.empty():
            name, event = self._queue.get_nowait()
            if name not in self._events:
                return

            for cb in self._events[name]:
                cb(event)

    def register(self, name, cb):
        """Register event callback."""
        if name not in self._events:
            self._events[name] = []

        self._events[name].append(cb)
        # print('Registering event: %s -%s' %(name,cb))
