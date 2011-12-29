import os, shutil


from yaml import load, dump
try:
    from yaml import CLoader as Loader
    from yaml import CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


import pin
pin.SETTINGS_ROOT = '/tmp/'
from pin import registry, util, event

def _destroy_settings():
    path = os.path.join(pin.SETTINGS_ROOT, pin.SETTINGS_FOLDER)
    shutil.rmtree(path)

CALLED = False

def _callback(*args, **kwargs):
    global CALLED
    CALLED = True

def test_event_register():
    event.register('test-cb', _callback)
    callbacks = event.get_events()
    assert 'test-cb' in callbacks
    assert _callback in callbacks['test-cb'] 

def test_event_fire():
    global CALLED
    CALLED = False
    event.fire('test-cb')
    assert CALLED == True

def test_event_unregister():
    event.unregister('test-cb', _callback)
    callbacks = event.get_events()
    assert _callback not in callbacks['test-cb']
