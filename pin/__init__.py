VERSION = '0.1dev'
PROJECT_FOLDER = '.pin'
SETTINGS_ROOT = '~'
SETTINGS_FOLDER = '.pinconf'
SETTINGS_FILE = 'settings.yml'
REGISTRY_FILE = 'registry.yml'
SHELL_FILE = 'source.sh'


def load_plugins():
    from straight.plugin import load
    load("pin.plugins")
