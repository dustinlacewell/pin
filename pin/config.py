import os

from yaml import load, dump
try:
    from yaml import CLoader as Loader
    from yaml import CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

from pin.util import get_project_root

CONFIG_NAME = "settings.yml"
GLOBAL_PATH = os.path.normpath(os.path.expanduser("~/.pinconf"))
DEFAULT_CONFIG = {}

def merge(user, default):
    if isinstance(user,dict) and isinstance(default,dict):
        for k,v in default.iteritems():
            if k not in user:
                user[k] = v
            else:
                user[k] = merge(user[k],v)
    return user

def load_yaml(path):
    config_file = open(path, 'r+')
    config = load(config_file, Loader=Loader)
    config_file.close()
    return config

def save_yaml(path, config):
    config_file = open(path, 'w')
    config_file.write(dump(config, default_flow_style=False))
    config_file.close()

def get_configuration():
    config = DEFAULT_CONFIG
    config = merge(load_yaml(os.path.join(GLOBAL_PATH, CONFIG_NAME)), config)
    # get project configuration
    root = get_project_root(os.getcwd())
    if root:
        configfile = os.path.join(root, '.pin', CONFIG_NAME)
        if os.path.isfile(configfile):
            config = merge(load_yaml(os.path.join(root, '.pin', CONFIG_NAME)), config)
    return config

config = get_configuration()
