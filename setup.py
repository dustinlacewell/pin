from distutils.core import setup

from pin import VERSION

setup(
    name='pin',
    version=VERSION,
    packages=['pin',],
    scripts=['bin/pin.sh', 'bin/__pin', ],
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    long_description=open('README.rst').read(),
)
