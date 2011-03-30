import os

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

