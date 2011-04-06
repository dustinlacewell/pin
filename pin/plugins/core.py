import os, shutil
from argparse import ArgumentParser

from pin import *
from pin.util import *
from pin import command, registry

class PinInitCommand(command.PinCommand):
    command = 'init'

    def raise_exists(self, path):
        msg = "Cannot initialize pin in an existing project: %s" % path
        print msg

    def execute(self, cwd, root):
        if root:
            self.raise_exists(root)
        else:
            print "Creating .pin directory structure..."
            registry.initialize_project(cwd)
            return True

    def done(self):
        print "pin project initialized in: %s" % os.getcwd()


command.register(PinInitCommand)

class PinDestroyCommand(command.PinCommand):
    command = 'destroy'

    def raise_no_project(self, path):
        msg = "No pin project found. (aborted)"
        print msg

    def execute(self, cwd, root):
        if not root:
            return self.raise_no_project(root)
        else:
            repeat = True
            while repeat:
                pinpath = os.path.join(root, PROJECT_FOLDERNAME)
                print "WARNING: Will destory all data in the .pin directory!"
                os.system("ls %s" % pinpath)
                selection = option_select(['y', 'n'], "Really destroy?")
                if selection == 'n':
                    print "Aborted."
                    return
                elif selection == 'y':
                    shutil.rmtree(pinpath)
                    registry.unregister(root)
                    return True
    def done(self):
        print "Pin project has been destroyed."

command.register(PinDestroyCommand)

class PinGoCommand(command.PinCommand):
    command = 'go'

    def setup_parser(self, parser):
        parser.add_argument('project', nargs="?")

    def execute(self, cwd, root):
        self.path = registry.pathfor(self.options.project)
        return self.path


    def write_script(self, file):
        if self.path:
            file.write("cd %s\n" % self.path)
        
command.register(PinGoCommand)
