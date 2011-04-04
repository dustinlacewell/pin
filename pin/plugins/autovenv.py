import os
from argparse import ArgumentParser

try:
    from capn.config import add_external_hook
    CAPN = True
except ImportError:
    CAPN = False

from pin.config import config
from pin.event import eventhook
from pin.plugin import PinHook, register
from pin.util import get_settings_path

# Capn auto-venv hooks

class CapnVenvPinHook(PinHook):

    name = "capn"
    default_hook_file = os.path.join(get_settings_path(), 'capnhooks')

    def __init__(self):
        self.options = None

    def _isactive(self):
        if self.options:
            return self.options.autoenv and self.options.venv
        return False
    active = property(_isactive)

    @eventhook('init-post-args')
    def postargs(self, args):
        parser = ArgumentParser()
        parser.add_argument('--autoenv', action='store_true')
        parser.add_argument('--venv', action='store_true')
        self.options, extargs = parser.parse_known_args(args)

    @eventhook('venv-post-create')
    def install(self, path, **kwargs):
        if self.active:
            activate_path = os.path.join(path, 'bin', 'activate')
            add_external_hook(self.default_hook_file, os.getcwd(), hooktype='tree',
                          enter=['source %s' % activate_path],
                          exit=['deactivate'], unique=True)

    @eventhook('init-post-script')
    def activate_capn(self, file):
        if self.active:
            file.write("source capn\n")
if CAPN:
    register(CapnVenvPinHook)
