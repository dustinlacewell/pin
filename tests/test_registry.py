import os, shutil


from yaml import load, dump
try:
    from yaml import CLoader as Loader
    from yaml import CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


import pin
pin.SETTINGS_ROOT = '/tmp/'
from pin import registry, util


def _destroy_settings():
    path = os.path.join(pin.SETTINGS_ROOT, pin.SETTINGS_FOLDER)
    shutil.rmtree(path)

def test_settings_testing_path():
    assert util.get_settings_path().startswith('/tmp')

def test_create_settings_folder():
    _destroy_settings()
    registry.establish_settings_folder()
    print "Checking '%s' exists..." % util.get_settings_path()
    assert os.path.exists(util.get_settings_path())
    print "Checking '%s' exists..." % util.get_settings_filename()
    assert os.path.isfile(util.get_settings_filename())
    print "Checking '%s' exists..." % util.get_registry_filename()
    assert os.path.isfile(util.get_registry_filename())

def test_create_registry():
    with open(util.get_registry_filename(), 'r') as file:
        _registry = load(file, Loader=Loader) or default
        assert 'projects' in _registry
        _projects = _registry['projects']
        assert isinstance(_projects, dict)

def test_load_registry():
    registry.load_registry()
    _projects = registry.get_registry()
    assert len(_projects) == 0
    assert isinstance(_projects, dict)

def test_register_path():
    registry.register('/tmp')
    assert '/tmp' in registry.get_registry()

def test_raw_pathfor():
    assert registry.pathfor('tmp') == '/tmp'

def test_unregister_path():
    registry.unregister('/tmp')
    assert '/tmp' not in registry.get_registry()

def test_register_alias_path():
    registry.register('/tmp', 'foobar')
    projects = registry.get_registry()
    assert '/tmp' in projects
    assert projects['/tmp']['alias'] == 'foobar'
    aliases = registry.get_aliases()
    assert 'foobar' in aliases
    assert aliases['foobar'] == '/tmp'

def test_unregister_alias_path():
    registry.unregister('/tmp')
    assert '/tmp' not in registry.get_registry()
    assert 'foobar' not in registry.get_aliases()

def test_register_save():
    registry.register('/tmp')
    registry.save_registry()
    with open(util.get_registry_filename(), 'r') as file:
        _registry = load(file, Loader=Loader) or default
        assert 'projects' in _registry
        _projects = _registry['projects']
        assert isinstance(_projects, dict)
        assert '/tmp' in _projects
    registry.unregister('/tmp')

def test_register_alias_save():
    registry.register('/tmp', 'foobar')
    registry.save_registry()
    with open(util.get_registry_filename(), 'r') as file:
        _registry = load(file, Loader=Loader) or default
        assert 'projects' in _registry
        _projects = _registry['projects']
        assert isinstance(_projects, dict)
        assert '/tmp' in _projects
        assert 'alias' in _projects['/tmp']
        assert 'foobar' == _projects['/tmp']['alias']

def test_name_is_registered():
    assert registry.name_is_registered('tmp')
    assert registry.name_is_registered('foobar')

def test_path_is_registered():
    assert registry.path_is_registered('/tmp')
    




    
