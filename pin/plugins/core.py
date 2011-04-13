import os, shutil
from argparse import ArgumentParser

from pin import *
from pin.util import *
from pin.delegate import CommandDelegator
from pin import command, registry

class PinInitCommand(command.PinCommand):
    '''
    Initialize pin in the current directory.
    '''
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
    '''
    Destroy and unregister the project from pin.
    '''
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
    '''
    Teleport to a specific project.
    '''
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

class PinHelpCommand(command.PinCommand):
    '''
    This help information.
    '''
    command = 'help'

    def setup_parser(self, parser):
        parser.add_argument('commandparts', nargs='*',
                            default=None)

    def process_simple_key(self, key, collen):
        comcls = command._commands[key]
        doc = comcls.__doc__ or ''
        print "{0: >{cl}}  - {1: ^24}".format(key, doc.strip(), cl=collen)

    def process_subcom_key(self, key, subcollen):
        if key in command._commands:
            subcomcls = command._commands[key]
            doc = subcomcls.__doc__ or ''
        else:
            try:
                key, doc = key
                doc = doc or ''
            except TypeError:
                doc = ''
        print "\t {0: >{scl}}  - {1: ^24}".format(key, doc.strip(), scl=subcollen)

    def process_container_key(self, key, collen, subcollen):
        comcls = command._commands[key]
        subcoms = getattr(comcls, 'subcommands', None)
        if not subcoms:
            self.process_simple_key(key, collen)
        else:
            print "{0: >{cl}}  -{1:-^{max}}".format(key, '',cl=collen, max=80-collen)
            if comcls.__doc__:
                print "{0: >{cl}}  {1}".format('', comcls.__doc__.strip(), cl=collen)
            for subkey in subcoms:
                self.process_subcom_key(subkey, subcollen)

    def do_default_help(self):
        CommandDelegator.parser.print_help()
        print "\nAvailable commands for %s:" % os.getcwd()
        comkeys = [k for k in command._commands.keys() if '-' not in k]
        maxlength = len(max(comkeys, key=len))
        simplekeys = [k for k in comkeys if not hasattr(command._commands[k], 'subcommands')]
        containerkeys = [k for k in comkeys if hasattr(command._commands[k], 'subcommands')]
        subcomkeys = []
        for com in containerkeys:
            contcom = command.get(com)
            for subcom, doc in contcom.subcommands:
                subcomkeys.append(subcom)
        submaxlength = len(max(subcomkeys, key=len))
        simplekeys.sort(); containerkeys.sort()
        for key in simplekeys:
            self.process_simple_key(key, collen=maxlength)
        for key in containerkeys:
            self.process_container_key(key, maxlength, submaxlength)
        

    def execute(self, cwd, root):
        if self.options.commandparts:
            clskey = '-'.join(self.options.commandparts)
            comcls = command.get(clskey)
            parser = comcls([])._getparser()
            parser.print_help()
        else:
            self.do_default_help()

command.register(PinHelpCommand)

