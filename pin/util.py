
import os, sys

from pin import *

class CompletionGenerator(object):

    def __init__(self):
        load_plugins()
        from pin import command, registry
        self.command = command
        self.registry = registry


        self.nargs = int(sys.argv[1]) - 1
        self.args = sys.argv[2:]

        self.completion = None

        self.comp_plain_command()
        if self.completion is None:
            self.comp_help_command()
        if self.completion is None:
            self.comp_all()

    def comp_plain_command(self):
        if self.nargs > 0:
            com_choices = self.check_command(self.args[0])
            if com_choices:
                if self.nargs == 1:
                    self.completion = " ".join(com_choices)
                elif self.nargs == 2 and len(com_choices) == 1:
                    com_name = com_choices[0]
                    subcom_choices = self.check_subcommand(com_name, 
                                                           self.args[1])
                    self.completion = " ".join(subcom_choices)

    def comp_help_command(self):
        if self.nargs > 0:
            if "help".startswith(self.args[0]):
                if self.nargs == 1:
                    self.completion = "help"
                else:
                    self.nargs -= 1
                    self.args = self.args[1:]
                    self.comp_plain_command()

    def comp_all(self):
        if self.nargs == 0:
            choices = []
            for com_name, com_cls in self.command.all().items():
                if com_cls([]).is_relevant():
                    choices.append(com_name)
            self.completion = " ".join(choices)


    def check_command(self, cmd):
        choices = []
        for cmd_name, cmd_cls in self.command.all().items():
            if cmd_name.startswith(cmd) and \
               cmd_cls([]).is_relevant():
                choices.append(cmd_name)
        return choices

    def check_subcommand(self, cmd, subcmd):
        choices = []
        cmd_cls = self.command.get(cmd)
        if hasattr(com_cls, 'get_subcommands'):
            subcmd_choices = cmd_cls.get_subcommands()
            if subcmd_choices:
                for sub in subcmd_choices:
                    name = sub.split('-')[-1]
                    if name.startswith(subcmd):
                        choices.append(subcmd)
        return choices
        

def compgen():
    '''Do command completion for bash.'''
    # requires plugins to be loaded
    load_plugins() 
    from pin import command, registry

    # get argument information
    nargs, args = int(sys.argv[1]), sys.argv[2:]

    """    
    The offset here is a pointer to the argument being
    completed. Since pin allows you to call commands
    against remote projects we need to adjust the
    completion algorithm accordingly. Each time another
    level of indirection is added, the offset is
    increased. A visual example is appropriate here. 

    The offset starts at 1:

    pin ini[tab] : off=1, nargs=1 - base command

    pin go mypro[tab] : off=1, nargs=2 - subcommand

    Indirections like help cause the offset to change:
    
    pin help destr[tab] : off=2, nargs=2 - base command

    pin help fab deplo[tab] : off=2, nargs=3 - subcommand

    So now the method of the algorithm is clear. If the
    offset is equal to the number of arguments, we know
    we need to complete a base command name. If the
    offset is one less than the number of arguments we
    know to complete a subcommand. Even with a project
    prefix this works:

    pin myproj help fab deplo[tab] :
       off   = (1 + myproj + help) = 3
       nargs = 4
       = subcommand!
    """
    off = 1
    proj_path = None
    # # # # # # # #
    # Project Name
    if args:
        proj_path = registry.pathfor(args[0], exact=False)
        # only increase the offset if we're not completing 
        # the first argument.
        if nargs > 1 and proj_path is not None:
            # increase the offset
            off += 1 
            # change to project directory
            os.chdir(proj_path)
    # # # # # # # #
    # Help command
    if args:
        # complete help command
        if nargs == off and "help".startswith(args[-1]):
            return 'help'
        # or increase offset by 1
        elif "help" in args:
            off += 1
    # # # # # # # #
    # base-command
    if nargs == off:
        arg = '' # default to empty arg
        if len(args) == off:
            # set working arg to item at offset
            arg = args[off-1]
        choices = " ".join([c for c in command._commands 
                            if c.startswith(arg)
                            and command.get(c)([]).is_relevant()])
        # return the choices if there are any
        if choices:
            return choices
        # we want commands to complete before
        # project names, so if we don't return any
        # choices above, complete a project name now
        # if we're completing the first argument
        if nargs == 1:
            if proj_path is not None:
                return os.path.basename(proj_path)
    # # # # # # # #
    # sub-commands
    elif nargs == off + 1:
        # get our parent command
        com = args[off-1]
        # get its class
        comcls = command.get(com)
        # if it is a delegate command
        if hasattr(comcls, 'get_subcommands'):
            # get partial subcommand name if user has typed anything
            # or else use empty string to complete all
            subcom = args[off] if len(args) == off+1 else ''
            # get a list of the parent command's subcommands
            subcom_choices = comcls.get_subcommands()
            # if there are any subcommands
            if subcom_choices:
                # clean subcommand names (they use command-subcommand format)
                choices = [k.split('-')[-1] for k in subcom_choices]
                # return the subcommands that start with the partial subcommand name
                return " ".join([c for c in choices if c.startswith(subcom)]) 
    # return nothing
    return ""

# def compgen():
#     gen = CompletionGenerator()
#     return gen.completion

def walkup(path):
    '''
    Walk through parent directories to root.
    '''
    at_top = False
    while not at_top:
        yield path
        parent_path = os.path.normpath(os.path.join(path, ".."))
        if parent_path == path:
            at_top = True
        else:
            path = parent_path

def name_from_path(path):
    return os.path.basename(path)

def get_settings_path():
    return os.path.expanduser(os.path.join("~", SETTINGS_FOLDER))

def path_has_project(path):
    '''
    Determine if supplied path contains the pin project
    directory.
    '''
    contents = os.listdir(path)
    if PROJECT_FOLDER in contents:
        return True

def get_project_root(path):
    '''
    Find the parent directory of the pin project, if 
    there is one.
    '''
    for directory in walkup(path):
        if path_has_project(directory):
            return directory

def get_settings_filename():
    return os.path.join(get_settings_path(), SETTINGS_FILE)

def get_registry_filename():
    return os.path.join(get_settings_path(), REGISTRY_FILE)
    
def get_sourcing_filename():
    return os.path.join(get_settings_path(), SHELL_FILE)

def findroot(fin):
    def fout(path):
        path = get_project_root(path)
        fin(path)
    return fout


def numeric_select(choices, prompt="Select from the above", title="Multiple choices possible:"):
    numeric_warning = False
    range_warning = False
    while True:
        print title
        for x in range(len(choices)):
            print " [%d] - %s" % (x + 1, str(choices[x]))
        if numeric_warning:
            print " ** Selection must be numeric"
            numeric_warning = False
        if range_warning:
            print " ** Selection must be in range"
        selection = raw_input(prompt + " [1 - %d]: " % len(choices))
        try:
            selection = int(selection)
        except ValueError:
            numeric_warning = True
        else:
            if selection >=1 and selection <= len(choices):
                return choices[selection-1]
            else:
                range_warning = True

def option_select(choices, prompt="Which choice?"):
    option_warning = False
    prompt = prompt + " [" + "/".join(choices) + "]:"
    while True:
        if option_warning:
            print " ** Input must be one of the options."
            option_warning = False
        selection = raw_input(prompt)
        if selection in choices:
            return selection
        else:
            option_warning = True

