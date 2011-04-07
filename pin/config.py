import os

from yaml import load, dump
try:
    from yaml import CLoader as Loader
    from yaml import CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

from pin.util import get_project_root

CONFIG_NAME = "settings.yml"
REGISTRY_NAME = "registry.yml"
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

def check_configuration():
    if not os.path.isdir(GLOBAL_PATH):
        os.mkdir(GLOBAL_PATH)
    configfile = os.path.join(GLOBAL_PATH, CONFIG_NAME)
    registryfile = os.path.join(GLOBAL_PATH, REGISTRY_NAME)
    os.open(configfile, os.O_CREAT)
    os.open(registryfile, os.O_CREAT)
        

def get_configuration():
    check_configuration()
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
