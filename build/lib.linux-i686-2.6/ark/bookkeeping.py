import os, sys

from ark import PROJECT_FOLDERNAME

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

def path_has_project(path):
    '''
    Determine if supplied path contains the ark project
    directory.
    '''
    contents = os.listdir(path)
    if PROJECT_FOLDERNAME in contents:
        return True

def get_project_root(path):
    '''
    Find the parent directory of the ark project, if 
    there is one.
    '''
    for directory in walkup(path):
        if path_has_project(directory):
            return directory


def initialize_project(path):
    if not path_has_project(path):
        project_path = os.path.join(path, PROJECT_FOLDERNAME)
        os.mkdir(project_path)
        with open(os.path.join(project_path, 'settings.yaml'), 'w'):
            pass
        msg = "ark project initialized in: %s" % project_path
        print msg
                 
        
