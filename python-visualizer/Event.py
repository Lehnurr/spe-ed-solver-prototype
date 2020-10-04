import threading


class Event:
    def __init__(self):
        self.listeners = []

    def __iadd__(self, listener):
        self.listeners.append(listener)
        return self

    def notify(self, *args):
        for listener in self.listeners:
            threading.Thread(target=listener, args=args).start()
