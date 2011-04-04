import os
from argparse import ArgumentParser

from pin import VERSION
from pin import command
from pin import plugin

class CommandDelegator(object):
    def __init__(self):
        self.delegate = False
        self.parser = self.get_argument_parser()
        self.args, self.exargs = self.parser.parse_known_args()

        if self.exargs:
            cmd, args = self.exargs[0], self.exargs[1:]
            self.do_delegation(cmd, args)
        else:
            self.do_default()

    def do_default(self):
        self.parser.print_help()

    def do_delegation(self, cmd, args):
        raise NotImplementedError

    def get_argument_parser(self):
        parser = ArgumentParser()
        parser.add_argument('-v', '--version', 
                            action='version', version=VERSION)
        return parser
        

class PinDelegator(CommandDelegator):

    def do_delegation(self, cmd, args):
        comcls = command.get(cmd)
        if comcls:
            comcls(args)._execute()
        else:
            self.do_default()
