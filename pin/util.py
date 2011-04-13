import os, sys

from pin import *

def compgen():
    '''
    Do command completion for bash. If first arg is
    'help', it is ignored and completion is done as 
    normal.
    '''
    load_plugins() # requires plugins to be loaded
    from pin import command
    nargs, args = int(sys.argv[1]), sys.argv[2:]
    off = 1 # delay ops one step if help is first arg
    if args and 'help'.startswith(args[0]):
        if nargs == 1:
            return 'help'
        off = 2
    if nargs == off: # first-level command
        arg = args[off-1] if len(args) == off else ''
        return " ".join([c for c in command._commands if c.startswith(arg)])
    elif nargs == off + 1: # subcommand
        com = args[off-1]
        comcls = command.get(com)
        subcom = args[off] if len(args) == off+1 else ''
        choices = [k.split('-')[-1] for k in comcls.get_subcommands()]
        prefix = comcls.command + '-' + subcom
        return " ".join([c for c in choices if c.startswith(subcom)]) 
    return ""

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
    return os.path.expanduser(os.path.join("~", SETTINGS_FOLDERNAME))

def path_has_project(path):
    '''
    Determine if supplied path contains the pin project
    directory.
    '''
    contents = os.listdir(path)
    if PROJECT_FOLDERNAME in contents:
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
    return os.path.join(get_settings_path(), SETTINGS_FILENAME)

def get_registry_filename():
    return os.path.join(get_settings_path(), REGISTRY_FILENAME)
    
def get_sourcing_filename():
    return os.path.join(get_settings_path(), SHELL_FILENAME)

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

