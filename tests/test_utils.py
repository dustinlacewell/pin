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
