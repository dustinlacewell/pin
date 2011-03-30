import os, sys, simplejson as json

from ark import *
from ark.util import *

def _name_from_path(path):
    return os.path.basename(path)

def _get_settings_path():
    return os.path.expanduser(os.path.join("~", SETTINGS_FOLDERNAME))

def _establish_settings_folder():
    '''
    Creates the ark user-settings folder if
    it does not exist.
    '''
    path = _get_settings_path()
    if not os.path.isdir(path):
        print "Creating settings folder"
        os.mkdir(path)
        os.mkdir(os.path.join(path, "templates"))
        with open(os.path.join(path, 'settings.json'), 'w'): pass

def _path_has_project(path):
    '''
    Determine if supplied path contains the ark project
    directory.
    '''
    contents = os.listdir(path)
    if PROJECT_FOLDERNAME in contents:
        return True

def _get_project_root(path):
    '''
    Find the parent directory of the ark project, if 
    there is one.
    '''
    for directory in walkup(path):
        if _path_has_project(directory):
            return directory

def _create_project_directory(path):
    project_path = os.path.join(path, PROJECT_FOLDERNAME)
    os.mkdir(project_path)
    os.mkdir(os.path.join(project_path, VIRTUALENV_FOLDERNAME))
    with open(os.path.join(project_path, 'settings.yaml'), 'w'): pass

def initialize_project(path):
    if not _get_project_root(path):
        msg = "ark project initialized in: %s" % project_path
        print msg

_establish_settings_folder()

#
# # Registry 
#

_projects = {}
_aliases = {}

def _get_registry_filename():
    return os.path.join(_get_settings_path(), 'projects.json')
    
def _create_registry():
    '''
    Create the registry file if it does not
    already exist.
    '''
    filename = _get_registry_filename()
    if not os.path.isfile(filename):
        with open(filename, 'w') as file:
            file.write(json.dumps({'projects': {}, 'aliases': {}}))
            
def _get_registry_file():
    filename = _get_registry_filename()
    return open(filename, 'r+')

def _load_registry():
    '''
    Load the registry from disk.
    '''
    projects_file = _get_registry_file()
    with projects_file:
        _registry = json.loads(projects_file.read())
        _projects = _registry['projects']
        _aliases = _registry['aliases']

def _save_registry():
    '''
    Save the registry to disk.
    '''
    projects_file = _get_registry_file()
    j = json.dumps({'projects': _projects})
    print j
    print projects_file
    projects_file.write(json.dumps({
                    'projects': _projects,
                    'aliases': _aliases}))

def _sync(fin):
    def fout(*args, **kwargs):
        _load_registry()
        fin(*args, **kwargs)
        _save_registry()
    return fout

@_sync
def is_registered(path):
    '''
    Returns whether a project path or alias
    are registered with ark.
    '''
    path = _aliases.get(path, path)
    return path in _projects

@_sync
def register(path, alias=None):
    '''
    Register a project path with optional alias
    with ark.
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
    msg = "ark initialized at: %s" % path
    if alias:
        _aliases[alias] = path
        msg = msg + " (%s)" % alias
    print msg

@_sync
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
    choices = [p for p in _projects if os.path.basename(p) == path]
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
            if selection > 1 and selection < len(choices):
                return choices[selection]

_create_registry() # initialize file if non-existant
_load_registry() # load data into module
