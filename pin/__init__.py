
VERSION = '0.1dev'
PROJECT_FOLDER = '.pin'
SETTINGS_FOLDER = '.pinconf'
SETTINGS_FILE = 'settings.yml'
REGISTRY_FILE = 'registry.yml'
SHELL_FILE = 'source.sh'

from straight.plugin import load as pluginloader

def load_plugins():
    pluginloader("pin.plugins")

