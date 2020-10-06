import threading

from config import NOTIFY_SIMULATED_PLAYER_ASYNC


class Event:
    def __init__(self):
        self.listeners = []

    def __iadd__(self, listener):
        self.listeners.append(listener)
        return self

    def notify(self, *args):
        for listener in self.listeners:
            if NOTIFY_SIMULATED_PLAYER_ASYNC:
                threading.Thread(target=listener, args=args).start()
            else:
                listener(*args)
