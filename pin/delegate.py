import os
from argparse import ArgumentParser

from pin import load_plugins
from pin import VERSION
from pin import command, registry

class CommandDelegator(object):
    parser = ArgumentParser(prog='pin', add_help=False)
    parser.add_argument('-v', '--version', 
                        action='version', version=VERSION)

    def __init__(self):
        self.delegate = False
        self.args, self.exargs = self.parser.parse_known_args()
        self.parser.add_argument('subcommand', nargs=1, default=None, 
                                 help='any subcommand available below')

        if self.exargs:
            cmd, args = self.exargs[0], self.exargs[1:]
        else:
            cmd, args = 'help', None
        self.do_delegation(cmd, args)

    def do_default(self):
        self.parser.print_help()

    def do_delegation(self, cmd, args):
        raise NotImplementedError

class PinDelegator(CommandDelegator):

    def do_delegation(self, cmd, args):
        load_plugins()
        # project precondition
        proj_path = registry.pathfor(cmd)
        if proj_path is not None:
            os.chdir(proj_path)
            cmd = args[0]
            args = args[1:]
        if '-' in cmd:
            cmd, newargs = cmd.split('-', 1)
            args = [newargs, ] + args
        comcls = command.get(cmd) or command.get('help')
        try:
            if comcls:
                comobj = comcls(args)
                if comobj.is_relevant():
                    comobj._execute()
                else:
                    helpcls = command.get('help')
                    helpobj = helpcls((cmd,))
                    helpobj._execute()
                    print "\n'%s %s' command not relevant here." % (cmd, args)
            else:
                self.do_default()
        except KeyboardInterrupt:
            print "\n"
            pass
