import os
from optparse import OptionParser

from ark import registry
from ark.env import create_virtualenv

_commands = {}

def register(cls, name):
    _commands[name] = cls

def get(name):
    return _commands.get(name, None)

class ArkCommand(object):
    def __init__(self, args):
        self.parser = self.get_parser()
        self.parser.parse_args()

    def get_parser(self):
        return OptionParser()

    def execute(self):
        pass

class ArkInitCommand(ArkCommand):

    def get_parser(self):
        parser = OptionParser()
        # set options here
        return parser

    def raise_exists(self, path):
        msg = "Cannot initialize ark in an existing project: %s" % path
        print msg

    def write_script(self):
        with open(os.path.expanduser("~/.arkconf/source.sh"), 'w') as file:
            file.write("source .ark/env/bin/activate\n")

    def execute(self):
        cwd = os.getcwd()
        root = registry.get_project_root(cwd)
        if root:
            self.raise_exists(root)
        else:
            print "Creating .ark directory structure..."
            registry.initialize_project(cwd)
            print "Creating virtualenv..."
            create_virtualenv(os.path.join(cwd, '.ark', 'env'))
            print "ark project initialized in: %s" % cwd
        self.write_script()

register(ArkInitCommand, 'init')
