import os, sys, pdb

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
        with open(os.path.join(path, SETTINGS_FILE), 'w'): pass
        create_registry()

def create_project_directory(path):
    project_path = os.path.join(path, PROJECT_FOLDER)
    os.mkdir(project_path)
    with open(os.path.join(project_path, SETTINGS_FILE), 'w'): pass

def initialize_project(path, alias=None):
    create_project_directory(path)
    register(path, alias)

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
            file.write(dump(dict(projects={})))

def load_registry():
    '''
    Load the registry from disk.
    '''
    global _projects, _aliases
    default = dict(projects={})
    with open(get_registry_filename(), 'r') as file:
        _registry = load(file, Loader=Loader) or default
        _projects = _registry['projects']
        for p, meta in _projects.iteritems():
            alias = meta.get('alias')
            if alias:
                _aliases[alias] = p

def get_registry():
    return _projects

def get_aliases():
    return _aliases

def save_registry():
    '''
    Save the registry to disk.
    '''
    with open(get_registry_filename(), 'w') as file:
        file.write(dump(dict(projects=_projects)))

def syncregistry(fin):
    def fout(*args, **kwargs):
        load_registry()
        ret = fin(*args, **kwargs)
        save_registry()
        return ret
    return fout

@syncregistry
def name_is_registered(name):
    '''
    Returns whether a project name or alias
    is registered with pin.
    '''
    return (name in _aliases
        or name in [os.path.basename(p) for p in _projects])

@syncregistry
def path_is_registered(path):
    '''
    Returns whether a project path
    is registered with pin.
    '''
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
                    
    if alias:
        _projects[path] = dict(alias=alias)
        _aliases[alias] = path
    else:
        _projects[path] = dict()

@syncregistry
def unregister(path):
    '''
    Unregister a project path with pin.
    '''
    if path in _projects:
        alias = _projects[path].get('alias')
        del _projects[path]
        if alias:
            del _aliases[alias]

@syncregistry
def pathfor(name, ask=False):
    '''
    Returns the full path of a project by 
    name or alias. If the name is not found
    None is returned.
    '''
    # Check aliases first
    choices  = [p for a, p in _aliases.items() if name and a.startswith(name)]
    # Enuemerate all projects in a folder `name`
    for p in _projects:
        if p not in choices:
            basename = os.path.basename(p)
            if os.path.basename(p).startswith(str(name)) or name is None:
                choices.append(p)
    n_choices = len(choices)
    if n_choices == 1: # return the only choice
        return choices[0]
    elif ask and n_choices > 0:
        # Get user to select choice
        return numeric_select(choices or  _projects.keys(), 
                              "Select path", "Select path")
        
