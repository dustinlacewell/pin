VERSION = '0.1dev'
PROJECT_FOLDERNAME = '.pin'
SETTINGS_FOLDERNAME = '.pinconf'
SETTINGS_FILENAME = 'settings.yml'
REGISTRY_FILENAME = 'registry.yml'
SHELL_FILENAME = 'source.sh'


def load_plugins():
    from straight.plugin import load
    load("pin.plugins")
