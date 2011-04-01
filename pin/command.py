import os
from argparse import ArgumentParser

from pin import registry
from pin.env import create_virtualenv

_commands = {}

def register(cls, name):
    _commands[name] = cls

def get(name):
    return _commands.get(name, None)

class PinCommand(object):

    listeners = []

    def __init__(self, args):
        self.parser = self.get_parser()
        for listener in self.listeners:
            
        self.options.parse_args()

    def get_parser(self):
        return ArgumentParser()

    def execute(self):
        pass

class PinInitCommand(PinCommand):

    def get_parser(self):
        parser = OptionParser()
        # set options here
        return parser

    def raise_exists(self, path):
        msg = "Cannot initialize pin in an existing project: %s" % path
        print msg

    def write_script(self):
        with open(os.path.expanduser("~/.pinconf/source.sh"), 'w') as file:
            file.write("source .pin/env/bin/activate\n")

    def execute(self):
        cwd = os.getcwd()
        root = registry.get_project_root(cwd)
        if root:
            self.raise_exists(root)
        else:
            print "Creating .pin directory structure..."
            registry.initialize_project(cwd)
            print "Creating virtualenv..."
            create_virtualenv(os.path.join(cwd, '.pin', 'env'))
            print "pin project initialized in: %s" % cwd
        self.write_script()

register(PinInitCommand, 'init')
