import os
import sys


config = None

def load_config():
    get_config()    # Load config if not loaded.

def get_config():
    global config
    if not config:
        config = create_default_config()
        config_file = look_up_config_file()
        if config_file:
            # NOTE: source_config_file() uses
            # exec statement (which is likely eval()).
            source_config_file(config_file, config)
    return config


def create_default_config():
    if sys.platform == 'win32':
        vim_home_dir = os.path.expanduser("~/vimfiles")
    else:
        vim_home_dir = os.path.expanduser("~/.vim")

    return {
        'vim_home_dir': vim_home_dir,
    }


def look_up_config_file():
    if os.environ.has_key('JOLT_RC'):
        if os.path.exists(os.environ['JOLT_RC']):
            return os.environ['JOLT_RC']
        else:
            return None

    if sys.platform == 'win32':
        path = []
        for env in ['HOME', 'USERPROFILE']:
            if os.environ.has_key(env):
                path.append(os.environ[env])
        path.append('.')
        filename = '_joltrc'
    else:
        assert os.environ.has_key('HOME')
        path = [os.environ['HOME']]
        filename = '.joltrc'

    for p in path:
        f = os.path.join(p, filename)
        if os.path.exists(f):
            return f

    return None

def source_config_file(config_file, config):
    with open(config_file) as f:
        exec f.read()
