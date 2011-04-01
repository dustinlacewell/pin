import os

from pin import *

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
    return os.path.join(get_settings_path(), 'settings.json')

def get_registry_filename():
    return os.path.join(get_settings_path(), 'projects.json')
    
def get_sourcing_filename():
    return os.path.join(get_settings_path(), 'source.sh')

def findroot(fin):
    def fout(path):
        path = get_project_root(path)
        fin(path)
    return fout
