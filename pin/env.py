import os

import virtualenv
virtualenv.logger = virtualenv.Logger(consumers=[])

from pin.util import *
from pin import registry

@findroot
def create_virtualenv(path):
    if path:
        path = os.path.join(path,
                            PROJECT_FOLDERNAME,
                            VIRTUALENV_FOLDERNAME)
        virtualenv.create_environment(path, False, True)

@findroot
def activate_virtualenv(path):
    if path:
        path = os.path.join(path,
                            PROJECT_FOLDERNAME,
                            VIRTUALENV_FOLDERNAME)
        settings = os.path.join(registry.get_settings_path(), 'source.sh')
        with open(settings, 'w') as file:
            file.write("source %s\n" % os.path.join(path, "bin/activate"))

def deactivate_virtualenv():
    settings = os.path.join(registry.get_settings_path(), 'source.sh')
    with open(settings, 'w') as file:
        file.write("deactivate\n")

@findroot
def auto_virtualenv(path):
    if path:
        activate_virtualenv(path)
    else:
        deactivate_virtualenv()




