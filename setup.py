import os

from setuptools import setup

from pin import VERSION

setup(
    name='pin',
    version="0.1.1",
    packages=['pin', 'pin.plugins'],
    scripts=['bin/pin.sh', 'bin/__pin', ],
    install_requires=['PyYAML', 'argparse'],
    provides=['pin'],
    author="Dustin Lacewell",
    author_email="dlacewell@gmail.com",
    url="https://github.com/dustinlacewell/pin",
    description="pin is a generic project management tool for the commandline.",
    long_description=open('README.markdown').read(),
)



