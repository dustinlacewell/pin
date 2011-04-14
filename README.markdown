pin
======

**pin** is a plugin-based command-line utility that helps you manage your software development projects. At it's core, it is a registry of where your projects reside on your file-system. Registering your project with **pin** lets you use utilize the various plugins. Since **pin** is generic, what this means exactly is based on what your project is and what plugins you have installed. 

### Installation 

    $ sudo pip install pin

### Usage

To use **pin** you will need to source it's shell-script which is installed under the name **pin.sh**:

    $ source pin.sh

The **pin** command will now be available to you. To see the core pin commands you can use the **help** command:

    $ pin help
    usage: pin [-v]
    
    optional arguments:
      -v, --version  show program's version number and exit
    
    Available commands for /home/dlacewell/dev/mine/pin:
    destroy  - Destroy and unregister the project from pin.
         go  - Teleport to a specific project.
       help  - This help information. 
       init  - Initialize pin in the current directory.
    $ 

Lets try out **pin init** in a new directory:

    $ mkdir /tmp/testing
    $ cd /tmp/testing
    $ pin init
    Creating .pin directory structure...
    pin project initialized in: /tmp/testing
    $

**pin** has created a project directory located at */tmp/testing/.pin/* **Generally, commands that operate upon your project can be used *anywhere* below the project's root directory**. **pin** doesn't do much on it's own but plugins can add new functionality to existing commands or new commands all together. Let's go ahead and install the *pin-venv* plugins to give **pin** the ability to work with *VirtualEnv*.

    $ sudo pip install pinvenv
    ...
    $ rm -fdr .pin/
    $ pin init --venv
    Creating .pin directory structure...
    Creating virtualenv...
    pin project initialized in: /tmp/testing
    $ ls .pin/env
    bin include lib
    $

### Core Commands

**pin init** : Initializes the .pin directory and registers the path with ~/.pinconf/registry.yml

**pin destroy** : Deletes the project's .pin directory and unregisters the project path. Only works from inside a project tree.

**pin go <project-name>** : Teleports to the project root if a name is provided. If no name is provided a menu will be presented.

**pin help** : Lists all pin commands including any provided by installed plugins.

### Plugins

Plugins to extend pin's core functionality can be found at the [Pin Cushion](https://github.com/dustinlacewell/pin/wiki/Pin-Cushion)
