
from straight.plugin import load

from pin import event

def register(hook):
    if hook not in _hooks:
        newhook = hook()
        newhook.register_hooks()
        _hooks.append(newhook)

def unregister(hook):
    if hook in _hooks:
        _hooks.remove()

class PinHook(object):

    name = None

    def __init__(self):
        pass

    def _isactive(self):
        return self.isactive()
    active = property(_isactive)

    def isactive(self):
        return True

    def fire(self, eventname, *args, **kwargs):
        event.fire(self.name + '-' + eventname, *args, **kwargs)

    def register_hooks(self):
        for attr in dir(self):
            attr = getattr(self, attr)
            eventname = getattr(attr, 'handled_event', None)
            if eventname:
                event.register(eventname, attr)

_hooks = []
load("pin.plugins")
