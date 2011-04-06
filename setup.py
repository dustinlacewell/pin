import os

from distutils.core import setup

from pin import VERSION

setup(
    name='pin',
    version="0.2",
    packages=['pin', 'pin.plugins'],
    scripts=['bin/pin.sh', 'bin/__pin', ],
    data_files=[(os.path.expanduser('~/.pinconf'), ['settings.yml'])],
    requires=['PyYAML', 'argparse'],
    author="Dustin Lacewell",
    author_email="dlacewell@gmail.com",
    url="https://github.com/dustinlacewell/pin",
    description="pin is a generic project management tool for the commandline.",
    long_description=open('README.markdown').read(),
)

user = os.path.basename(os.path.expanduser("~"))
os.system('chown -R %s:%s %s' % (user, user, os.path.expanduser("~/.pinconf")))
