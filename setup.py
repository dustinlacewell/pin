from distutils.core import setup

from ark import VERSION

setup(
    name='ark',
    version=VERSION,
    packages=['ark',],
    scripts=['bin/ark.sh', 'bin/__ark', 'bin/__arkauto'],
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    long_description=open('README.rst').read(),
)
