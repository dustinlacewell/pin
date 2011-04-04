pin
======

**pin** is a set of Python scripts that help you streamline your use of deployment tools.

### Installation 

    $ sudo apt-get install python-yaml
    $ sudo pip install straight.plugin
    $ sudo python setup.py install

### Usage

To use **pin** you will need to source it's shell-script which is installed under the name **pin.sh**

    $ source pin.sh

The **pin** command will now be available to you. Lets try out **pin** in a new directory.

    $ mkdir /tmp/testing
    $ cd /tmp/testing
    $ pin init
    Creating .pin directory structure...
    pin project initialized in: /tmp/testing
    $

**pin** has created a project directory located at */tmp/testing/.pin/* **pin** doesn't do much on it's own but plugins can add functionality to existing command or new commands all together. Let's go ahead and install the *pin-venv* plugins to give **pin** the ability to work with *VirtualEnv*.

    $ sudo pip install pin-venv
    ...
    $ rm -fdr .pin/
    $ pin init --venv
    Creating .pin directory structure...
    Creating virtualenv...
    pin project initialized in: /tmp/testing
    $ ls .pin/env
    bin include lib
    $





