import os, sys
from argparse import ArgumentParser

from pin import event
from pin.util import get_project_root

_commands = {}

def register(cls):
    _commands[cls.command] = cls

def get(name):
    return _commands.get(name, None)

def all():
    return _commands

class PinCommand(object):
    command = None

    def __init__(self, args):
        self.args = args
        self.parser = self._getparser()
        self.options = self._getoptions(args)

    def fire(self, name, *args, **kwargs):
        event.fire(self.command + '-' + name, *args, **kwargs)

    def _getparser(self):
        parser = ArgumentParser(prog='pin ' + self.command, add_help=False)
        self.fire('pre-parser', parser)
        self.setup_parser(parser)
        self.fire('post-parser', parser)
        return parser

    def _getoptions(self, args):
        self.fire('pre-args', args)
        options, extargs = self.parser.parse_known_args(args)
        self.fire('post-args', extargs)
        return options

    def _writescript(self):
        with open(os.path.expanduser("~/.pinconf/source.sh"), 'w') as file:
            self.fire('pre-script', file)
            self.write_script(file)
            self.fire('post-script', file)

    def _execute(self):
        cwd = os.getcwd()
        root = get_project_root(cwd)
        self.fire('pre-exec', cwd, root)
        success = self.execute(cwd, root)
        if success:
            self.fire('post-exec', cwd, root)
            self._writescript()
            self.done()


    def setup_parser(self, parser):
        pass

    def write_script(self, file):
        pass

    def execute(self, cwd, root):
        pass

    def done(self):
        pass


class PinBaseCommandDelegator(PinCommand):
    subcommands = [] # handled commands

    def _getparser(self):
        '''
        Adds an implicit 'subcommand' argument.
        '''
        parser = ArgumentParser(prog='pin ' + self.command, add_help=False)
        self.fire('pre-parser', parser)
        parser.add_argument('subcommand', nargs='?', 
                            choices=[c[0].split('-')[-1] for c in self.subcommands],
                            default=None)

        self.setup_parser(parser)
        self.fire('post-parser', parser)
        return parser

    @classmethod
    def get_subcommands(cls):
        raise NotImplementedError

class PinPluginCommandDelegator(PinBaseCommandDelegator):
    def _execute(self):
        cwd = os.getcwd()
        root = get_project_root(cwd)
        self.fire('pre-exec', cwd, root)
        if self.options.subcommand:
            clskey = self.command + '-' + self.options.subcommand
            comcls = get(clskey)
            success = comcls(self.args[1:])._execute()
        else:
            success = self.execute(cwd, root)
        if success:
            self.fire('post-exec', cwd, root)
            self._writescript()
            self.done()

    @classmethod
    def get_subcommands(cls):
        return dict((c, get(c)) for c in cls.subcommands)

    

