import os
from argparse import ArgumentParser

from pin import event

_commands = {}

def register(cls):
    _commands[cls.command] = cls

def get(name):
    return _commands.get(name, None)

class PinCommand(object):
    command = None

    def __init__(self, args):
        self.parser = self._getparser()
        self.options = self._getoptions(args)

    def fire(self, name, *args, **kwargs):
        event.fire(self.command + '-' + name, *args, **kwargs)

    def _getparser(self):
        parser = ArgumentParser()
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
        self.fire('pre-exec', cwd)
        writescript = self.execute()
        self.fire('post-exec', cwd)
        if writescript:
            self._writescript()
        self.done()


    def setup_parser(self, parser):
        pass

    def write_script(self, file):
        pass

    def execute(self):
        pass

    def done(self):
        pass

