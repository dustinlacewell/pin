import os
from argparse import ArgumentParser

from ark import VERSION
from ark import command

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
        

class ArkDelegator(CommandDelegator):

    def do_delegation(self, cmd, args):
        comcls = command.get(cmd)
        if comcls:
            comcls(args).execute()
        else:
            self.do_default()
