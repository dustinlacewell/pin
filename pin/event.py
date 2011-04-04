
_events = {}

def register(name, callback):
    eventset = _events.get(name, set([]))
    eventset.add(callback)
    _events[name] = eventset

def unregister(name, callback):
    eventset = _events.get(name)
    if eventset and callback in eventset:
        eventset.remove(callback)
        _events[name] = eventset

def fire(name, *args, **kwargs):
    eventset = _events.get(name)
    if eventset:
        for handler in eventset:
            handler(*args, **kwargs)

class eventhook(object):
    def __init__(self, eventname):
        self.eventname = eventname
        
    def __call__(self, f):
        def wrapped_f(*args, **kwargs):
            f(*args, **kwargs)
        wrapped_f.handled_event = self.eventname
        return wrapped_f
