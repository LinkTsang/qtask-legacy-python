class Observable:
    def __init__(self):
        self.callbacks = []

    def on(self, callback):
        self.callbacks.append(callback)

    def off(self, callback):
        self.callbacks.remove(callback)

    def fire(self, *args, **kwargs):
        for callback in self.callbacks:
            callback(*args, **kwargs)
