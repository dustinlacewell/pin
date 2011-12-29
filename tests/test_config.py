import os, shutil


from yaml import load, dump
try:
    from yaml import CLoader as Loader
    from yaml import CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


import pin
pin.SETTINGS_ROOT = '/tmp/'
from pin import registry, util, config

def _destroy_settings():
    path = os.path.join(pin.SETTINGS_ROOT, pin.SETTINGS_FOLDER)
    shutil.rmtree(path)


def test_settings_merge():
    a = {'1':'a', '2':'b', '3':[1,2,3]}
    b = {'1':'a', '3':[4,5,6]}    
    c = config.merge(b, a)
    assert c['3'] == [4,5,6]
    assert c['2'] == 'b'




