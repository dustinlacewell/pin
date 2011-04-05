import os
from argparse import ArgumentParser

from pin import command, registry

class PinInitCommand(command.PinCommand):
    command = 'init'

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


class PinGoCommand(command.PinCommand):
    command = 'go'

    def setup_parser(self, parser):
        parser.add_argument('project', nargs="?")

    def execute(self):
        self.path = registry.pathfor(self.options.project)
        return self.path


    def write_script(self, file):
        if self.path:
            file.write("cd %s\n" % self.path)
        
command.register(PinGoCommand)
