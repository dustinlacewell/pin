import os

from distutils.core import setup

from pin import VERSION

setup(
    name='pin',
    version=VERSION,
    packages=['pin', 'pin.plugins'],
    scripts=['bin/pin.sh', 'bin/__pin', ],
    data_files=[(os.path.expanduser('~/.pinconf'), ['settings.yml'])],
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    long_description=open('README.markdown').read(),
)

user = os.path.basename(os.path.expanduser("~"))
os.system('chown -R %s:%s %s' % (user, user, os.path.expanduser("~/.pinconf")))
