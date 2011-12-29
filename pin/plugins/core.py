import os, shutil, pdb
from argparse import ArgumentParser

from pin import *
from pin.util import *
from pin.delegate import CommandDelegator
from pin import command, registry

class PinInitCommand(command.PinCommand):
    '''Initialize pin in the current directory.'''

    command = 'init'

    def is_relevant(self):
        return not self.root

    def setup_parser(self, parser):
        parser.add_argument('--alias', nargs=1, default=None, metavar='alias')

    def raise_exists(self):
        msg = "Cannot initialize pin in an existing project: %s" % self.cwd
        print msg

    def execute(self):
        if self.root:
            self.raise_exists()
        else:
            print "Creating .pin directory structure..."
            alias = None
            if self.options.alias:
                alias = self.options.alias[0]
            registry.initialize_project(self.cwd, alias=alias)
            self.root = self.cwd
            return True

    def done(self):
        print "pin project initialized in: %s" % self.cwd
command.register(PinInitCommand)



class PinDestroyCommand(command.PinCommand):
    '''Destroy and unregister the project from pin.'''

    command = 'destroy'

    def is_relevant(self):
        return self.root

    def raise_no_project(self):
        msg = "No pin project found. (aborted)"
        print msg

    def execute(self):
        if not self.root:
            return self.raise_no_project()
        else:
            repeat = True
            while repeat:
                pinpath = os.path.join(self.root, PROJECT_FOLDER)
                print "WARNING: Will destory all data in the .pin directory!"
                os.system("ls %s" % pinpath)
                selection = option_select(['y', 'n'], "Really destroy?")
                if selection == 'n':
                    print "Aborted."
                    return
                elif selection == 'y':
                    shutil.rmtree(pinpath)
                    registry.unregister(self.root)
                    return True
    def done(self):
        print "Pin project has been destroyed."

command.register(PinDestroyCommand)

class PinProjectProxy(object):
    '''Pin project project used for Go command'''
    
    def __init__(self, path):
        self.__doc__ = path


class PinGoCommand(command.PinCommand):
    '''
    Teleport to a specific project.
    '''
    command = 'go'

    def setup_parser(self, parser):
        
        parser.add_argument('project', nargs="?")

    def execute(self):
        self.path = registry.pathfor(self.options.project, ask=True)
        return self.path

    def write_script(self, file):
        if self.path:
            file.write("cd %s\n" % self.path)
        
    @classmethod
    def get_subcommands(cls):
        subs = dict()
        for p, meta in registry._projects.items():
            alias = meta.get('alias')
            if alias:
                subs[alias] = PinProjectProxy(p)
            else:
                subs[os.path.basename(p)] = PinProjectProxy(p)
        return subs

command.register(PinGoCommand)

class PinAliasCommand(command.PinCommand):
    '''Manage project aliases'''

    command = 'alias'

    def setup_parser(self, parser):
        parser.add_argument('name', nargs="?")
        parser.add_argument('-p', '--proj', nargs="?", dest='project')


    def execute(self):
#        pdb.set_trace()
        name = self.options.name
        project = getattr(self.options, 'project', None)
        if project:
            proj_path = registry.pathfor(project)
            if not proj_path:
                print "* Project", project, "not found."
                return
        elif self.root:
            proj_path = self.root
        else:
            print "Must provide -p/--project option, if outside of pin project."
            return
        if name in registry._aliases:
            if proj_path != registry._aliases[name]:
                print "Alias `{alias}' already exists for other project:".format(alias=name)
                print registry._aliases[name]
                return
            else:
                print "Alias `{alias}' already set.".format(alias=name)
                return
        else:
            current_alias = registry._projects[proj_path].get('alias')
            if current_alias:
                prompt =  "Alias `{alias}' already set, overwrite?".format(alias=current_alias)
                answer = option_select(['y','n'], prompt)
                if answer == 'n':
                    print "Aborted."
                    return
                
            _projects[proj_path]['alias'] = name
            _aliases[name] = proj_path
            registry.save_registry()
            print "Alias `{alias}' has been set for, {path}".format(alias=name,
                                                                    path=proj_path)
            return True
                    
command.register(PinAliasCommand)
    

class PinHelpCommand(command.PinCommand):
    '''This help information.'''

    command = 'help'

    def setup_parser(self, parser):
        parser.add_argument('command', nargs='*',
                            default=None)
        parser.add_argument('-a', '--all', dest='all', action='store_true')

    def process_simplecom(self, name, collen):
        comcls = command.get(name)
        comobj = comcls([])
        if comobj.is_relevant() or self.options.all:
            usage = comobj.parser.format_usage().replace("usage: ", "")
            doc = comcls.__doc__ or ''
            print "{0: >{cl}}  - {1: ^24}".format(usage,
                                                  doc.strip(), 
                                                  cl=collen)

    def process_subcom(self, name, subcom, subcollen):
        doc = subcom.__doc__ or ''
        name = name.split('-')[-1]
        print "    {0: >{scl}}  - {1: ^24}".format(name, doc.strip(), scl=subcollen)

    def process_containercom(self, name, collen, subcollen):
        comcls = command.get(name)
        comobj = comcls([])
        usage = comobj.parser.format_usage().replace("usage: ", "")
        print usage.strip()
        if hasattr(comcls, 'get_subcommands'):
            if comcls.__doc__:
                print "{0} {1}".format(' - ', comcls.__doc__.strip(), cl=collen)
            subcoms = comcls.get_subcommands()
            if subcoms:
                for name, subcom in subcoms.items():
                    self.process_subcom(name, subcom, subcollen)

    def do_default_help(self):
        '''
        Render pin's general help

        This method will iterate through all available commands that declare
        themselves as being 'relevant'. Some processing is done to determine
        formatting widths of the output and help for delegate-commands 
        that contain subcommands are dynamically computed.
        '''
        # print generic pin help
        CommandDelegator.parser.print_help()
        comkeys = [k for k in command.all().keys() if '-' not in k]
        maxlength = len(max(comkeys, key=len))
        simplekeys = [] # commands without subcommands
        containerkeys = [] # subcommand delgates
        subcomkeys = []
        submaxlength = maxlength
        # iterate over all commands
        for k in comkeys:
            # get command class
            comcls = command.get(k)
            # get dummy instance
            comobj = comcls([])
            # check if command is relevant
            if comobj.is_relevant() or self.options.all:
                # add to specific list based on `get_subcommands' attribute
                if hasattr(comcls, 'get_subcommands'):
                    containerkeys.append(k)
                    # grab all subcommand keys
                    subcoms = comcls.get_subcommands()
                    if subcoms:
                        subcomkeys += subcoms.keys()
                else:
                    simplekeys.append(k)
        # calculate global max-length of subcommand keys
        if subcomkeys:
            submaxlength = len(max(subcomkeys, key=len))
        # sort all keys
        simplekeys.sort(); containerkeys.sort()
        if simplekeys or containerkeys:
            print "Available commands for %s:" % os.getcwd()
            # render simplekeys, then containerkeys
            for key in simplekeys:
                self.process_simplecom(key, maxlength)
            for key in containerkeys:
                self.process_containercom(key, maxlength, submaxlength)
        

    def execute(self):
        if self.options.command:
            clskey = '-'.join(self.options.command)
            comcls = command.get(clskey)
            if comcls: # if args point to pin command
                comobj = comcls([])
                parser = comobj.parser
                parser.print_help()
                if hasattr(comcls, 'get_subcommands'):
                    subcoms = comcls.get_subcommands() 
                    if subcoms:
                        submaxlength = len(max(subcoms.keys(), key=len))
                        for name, subcom in subcoms.items():
                            self.process_subcom(name, subcom, submaxlength)
            else: # ask parent command
                pcomcls = command.get(self.options.command[0])
                if pcomcls and hasattr(pcomcls, 'get_subcommands'):
                    subcommands = pcomcls.get_subcommands()
                    if subcommands:
                        for name, com in subcommands.items():
                            if name == self.options.command[1]:
                                print com.__doc__ or 'Command has no docstring.'
                else:
                    self.do_default_help()

                    
            
        else:
            self.do_default_help()

command.register(PinHelpCommand)

