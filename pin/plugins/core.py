import os
from argparse import ArgumentParser

from pin import command, registry

class PinInitCommand(command.PinCommand):
    command = 'init'

    def get_parser(self):
        parser = ArgumentParser()
        # set options here
        return parser

    def raise_exists(self, path):
        msg = "Cannot initialize pin in an existing project: %s" % path
        print msg

    def execute(self):
        cwd = os.getcwd()
        root = registry.get_project_root(cwd)
        if root:
            self.raise_exists(root)
        else:
            print "Creating .pin directory structure..."
            registry.initialize_project(cwd)
            return True

    def done(self):
        print "pin project initialized in: %s" % os.getcwd()


command.register(PinInitCommand)
