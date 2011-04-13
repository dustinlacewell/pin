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

    def process_simplecom(self, name, collen):
        comcls = command.get(name)
        doc = comcls.__doc__ or ''
        print "{0: >{cl}}  - {1: ^24}".format(name, doc.strip(), cl=collen)

    def process_subcom(self, name, subcom, subcollen):
        doc = subcom.__doc__ or ''
        print "\t {0: >{scl}}  - {1: ^24}".format(name, doc.strip(), scl=subcollen)

    def process_containercom(self, name, collen, subcollen):
        comcls = command.get(name)
        subcoms = comcls.get_subcommands()
        print "{0: >{cl}}  -{1:-^{max}}".format(name, '',cl=collen, max=80-collen)
        if comcls.__doc__:
            print "{0: >{cl}}  {1}".format('', comcls.__doc__.strip(), cl=collen)
        for name, subcom in subcoms.items():
            self.process_subcom(name, subcom, subcollen)

    def do_default_help(self):
        CommandDelegator.parser.print_help()
        print "\nAvailable commands for %s:" % os.getcwd()
        comkeys = [k for k in command.all().keys() if '-' not in k]
        maxlength = len(max(comkeys, key=len))
        simplekeys = [k for k in comkeys if not hasattr(command.get(k), 'get_subcommands')]
        containerkeys = [k for k in comkeys if hasattr(command.get(k), 'get_subcommands')]
        if containerkeys:
            subcomkeys = []
            for com in containerkeys:
                comcls = command.get(com)
                print com, comcls
                for name, subcomcls in comcls.get_subcommands().items():
                    print name
                    subcomkeys.append(name)
            submaxlength = len(max(subcomkeys, key=len))
        simplekeys.sort(); containerkeys.sort()
        for key in simplekeys:
            self.process_simplecom(key, collen=maxlength)
        for key in containerkeys:
            self.process_containercom(key, maxlength, submaxlength)
        

    def execute(self, cwd, root):
        if self.options.commandparts:
            clskey = '-'.join(self.options.commandparts)
            comcls = command.get(clskey)
            if comcls: # if args point to pin command
                parser = comcls([])._getparser()
                parser.print_help()
            else: # ask parent command
                pcomcls = command.get(self.options.commandparts[0])
                subcommands = pcomcls.get_subcommands()
                if subcommands:
                    for name, com in subcommands.items():
                        if name == self.options.commandparts[1]:
                            print com.__doc__ or 'Command has no docstring.'
                    
            
        else:
            self.do_default_help()

command.register(PinHelpCommand)

