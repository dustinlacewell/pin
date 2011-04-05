import os, sys

from yaml import load, dump
try:
    from yaml import CLoader as Loader
    from yaml import CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


from pin import *
from pin.util import *

def establish_settings_folder():
    '''
    Creates the pin user-settings folder if
    it does not exist.
    '''
    path = get_settings_path()
    if not os.path.isdir(path):
        os.mkdir(path)
        with open(os.path.join(path, SETTINGS_FILENAME), 'w'): pass
        with open(os.path.join(path, REGISTRY_FILENAME), 'w'): pass

def create_project_directory(path):
    project_path = os.path.join(path, PROJECT_FOLDERNAME)
    os.mkdir(project_path)
    with open(os.path.join(project_path, SETTINGS_FILENAME), 'w'): pass

def initialize_project(path, alias=None):
    if not get_project_root(path):
        create_project_directory(path)
        register(path, alias)

establish_settings_folder()

#
# # Registry 
#

_projects = {}
_aliases = {}

def create_registry():
    '''
    Create the registry file if it does not
    already exist.
    '''
    filename = get_registry_filename()
    if not os.path.isfile(filename):
        with open(filename, 'w') as file:
            file.write(dump({'projects': {}, 'aliases': {}}))

def load_registry():
    '''
    Load the registry from disk.
    '''
    global _projects, _aliases
    with open(get_registry_filename(), 'r') as file:
        _registry = load(file, Loader=Loader)
        _projects = _registry['projects']
        _aliases = _registry['aliases']

def save_registry():
    '''
    Save the registry to disk.
    '''
    with open(get_registry_filename(), 'w') as file:
        j = dump({'projects': _projects})
        file.write(dump({
                    'projects': _projects,
                    'aliases': _aliases}))

def syncregistry(fin):
    def fout(*args, **kwargs):
        load_registry()
        ret = fin(*args, **kwargs)
        save_registry()
        return ret
    return fout

@syncregistry
def is_registered(path):
    '''
    Returns whether a project path or alias
    are registered with pin.
    '''
    path = _aliases.get(path, path)
    return path in _projects

@syncregistry
def register(path, alias=None):
    '''
    Register a project path with optional alias
    with pin.
    '''
    if alias in _aliases:
        msg = "Alias, %s, already exists. Overwrite? [y/n] " % alias
        repeat = True
        while repeat:
            overwrite = raw_input(msg).strip().lower()[0]
            if overwrite in ['y', 'n']:
                repeat = False
                if overwrite == 'n':
                    print "*** Alias ignored."
                    alias = None
                    
    _projects[path] = {}
    if alias:
        _aliases[alias] = path

@syncregistry
def unregister(path):
    '''
    Unregister a project path with pin.
    '''
    del _projects[path]
    removedaliases = []
    for alias, apath in _aliases:
        if apath == path:
            removedaliases.append(alias)
    for alias in removedaliases:
        del _aliases[alias]

@syncregistry
def pathfor(name):
    '''
    Returns the full path of a project by 
    name or alias. If the name is not found
    None is returned.
    '''
    # Check aliases first
    path = _aliases.get(name, None)
    if path and is_registered(path):
        return path
    # Enuemerate all projects in a folder `name`
    choices = [p for p in _projects if os.path.basename(p) == name or name is None]
    if len(choices) == 1: # return the only choice
        return choices[0]
    # Get user to select choice
    repeat = True
    warning = False
    while repeat:
        print "Multiple projects possible:"
        for x in range(len(choices)):
            print " [%d] - %s" % (x + 1, choices[x])
        if warning:
            print " ** Selection must be numeric"
            warning = False
        selection = raw_input("Go to [1 - %d]:" % len(choices))
        try:
            selection = int(selection)
        except ValueError:
            warning = True
        else:
            if selection >= 1 and selection <= len(choices):
                return choices[selection-1]

create_registry() # initialize file if non-existant
load_registry() # load data into module
