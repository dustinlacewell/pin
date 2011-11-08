import os, sys
from argparse import ArgumentParser

from pin import event
from pin.util import get_project_root

_commands = {}

def register(cls):
    '''Register class as available command'''
    _commands[cls.command] = cls

def get(name):
    '''Get command-class by name'''
    return _commands.get(name, None)

def all():
    '''Return a dictionary of all available commands'''
    return _commands

class PinCommand(object):
    '''
    A Pin command

    PinCommands represent actions that can be performed. Commands may 
    fire any number of events including the standard events listed below.

    attributes:
      cwd : path where command was executed
      root : root path of pin-project if one exists
      args : list of passed command arguments
      parser : command specific argparse.ArgumentParser
      options : result of argument parsing

    Hookable events allow PinHooks to respond to or modify the behavior
    of PinCommands. Plugins may radically change the way other plugin or
    even standard commands work. 

    Each event has a pre and post version.
    For example, the `exec' event may be hooked by `pre-exec' or `post-exec'
    depending on what you want to do.

    Some hooks are passed valuable data related to the event that may be
    modified to change the behavior of the event.

    standard hookable events:
      `parser' : 
      -- When command configures its argument parser
      -- Args :
         parser - the ArgumentParser
        
      `args' :
      -- When argument parsing takes place
      -- Args:
         args - User supplied arguments to the command

      `script' :
      -- As the external sourcing script is generated
      -- Args:
         file - File object representing the script to be generated

      `exec' :
      -- When the command executes its work
      -- Args:
         cwd - the directory path the command was executed in
         root - the root path of the pin project, if one exists

    overridable methods:
      is_relevant, setup_parser, write_script, execute, done
    '''

    command = None

    def __init__(self, args):
        # get current working directory
        self.cwd = os.getcwd()
        # find out if this is a pin project
        self.root = get_project_root(self.cwd)
        self.args = args
        # get command's argument-parser
        self.parser = self._getparser()
        # get command's parsed arguments
        self.options = self._getoptions(args)

    def fire(self, name, *args, **kwargs):
        '''
        Fire an arbitrary event

        Event names, by convention, should be lower-case-and-hypen-seperated.
        When events are hooked, the command that emitted the event will
        have its name prepended in this way. 

        For example, before the InitCommand executes it will fire an event 
        that can be handled by the name 'init-pre-exec' for an event fired 
        with the name 'pre-exec'.
        '''
        event.fire(self.command + '-' + name, *args, **kwargs)

    def _getparser(self):
        parser = ArgumentParser(prog='pin ' + self.command, add_help=False)
        if self.__doc__:
            parser.description = self.__doc__.splitlines()[0]
        self.fire('pre-parser', parser)
        self.setup_parser(parser)
        self.fire('post-parser', parser)
        return parser

    def _getoptions(self, args):
        self.fire('pre-args', args)
        options, extargs = self.parser.parse_known_args(args)
        self.fire('post-args', extargs, options)
        return options

    def _writescript(self):
        with open(os.path.expanduser("~/.pinconf/source.sh"), 'w') as file:
            self.fire('pre-script', file)
            self.write_script(file)
            self.fire('post-script', file)

    def _execute(self):
        self.fire('pre-exec', self.cwd, self.root)
        success = self.execute()
        if success:
            self.fire('post-exec', self.cwd, self.root)
            self._writescript()
            self.done()

    def is_relevant(self):
        '''
        Determines whether or not the command is visible in the current context.
        '''
        return True

    def setup_parser(self, parser):
        '''
        User overridable method for configuring the command's ArgumentParser.
        '''
        pass

    def write_script(self, file):
        '''
        User overridable method for writing out any nessecary post-execution
        bash code.
        '''
        pass

    def execute(self):
        '''
        User overridable method for implementing the actual work of the command.
        '''
        pass

    def done(self):
        '''
        User overridable method for work done after command has completed.
        '''
        pass


class PinSubCommand(PinCommand):
    def is_relevant(self):
        return False

class PinDelegateCommand(PinCommand):
    subcommands = [] # handled commands

    def _getparser(self):
        '''
        Adds an implicit 'subcommand' argument.
        '''
        parser = ArgumentParser(prog='pin ' + self.command, add_help=False)
        parser.add_argument('subcommand', nargs='*')
        self.fire('pre-parser', parser)
        self.setup_parser(parser)
        self.fire('post-parser', parser)
        return parser

    def _execute(self):
        success = False
        if self.options.subcommand:
            for subcom in self.subcommands:
                if subcom.command == '-'.join((self.command, self.options.subcommand[0])):
                    subcom(self.args[1:])._execute()
                    return
            self.fire('pre-exec', self.cwd, self.root)
            success = self.execute()
        else:
            self.fire('pre-exec', self.cwd, self.root)
            success = self.execute()
        if success:
            self.fire('post-exec', self.cwd, self.root)
            self._writescript()
            self.done()

    @classmethod
    def get_subcommands(cls):
        return dict((c.command, c) for c in cls.subcommands)

    

