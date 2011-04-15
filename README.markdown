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


### Writing Plugins

Plugins for **pin** are packaged as Namespace packages. Ensure that your plugin package resembles the following structure:

    yourpackage/
      setup.py
      requirements.tx
      README
      pin/
        __init__.py
        plugins/
          __init__.py
          yourpackage.py

To make your package namespaced you will need to add the following lines to each of the two **__init__.py** files:

    import pkg_resources
    pkg_resources.declare_namespace(__name__)

The two plugin-classes that you can register with pip are **commands** and **hooks**. Before covering those specifically, let's review some notable API available for plugins to use:

### Utility API

 * **util.path_has_project(path)** : Determine if the supplied path contains the pin project-directory.

 * **util.get_project_root(path)** : Find the root project directory for the path, if there is one.

 * **util.get_settings_filename()** : Get the absolute path to the pin settings YAML file

 * **util.get_registry_filename()** : Get the absolute path to the pin registry YAML file


### Writing Commands

The base command class is **command.Pincommand**. Your command will be a subclass that you register with **command.register(cls)**. There are a number of methods that you can override to define the behavior of your command. At minimum your class needs to define a class-attribute '**command**' which is the name of your command. Let's write a simple command called '*check*' the determines if the current-working-directory is inside of a pin project:

    class CheckCommand(command.PinCommand):
        command = 'check'

Just to illustrate the proper way to handle arguments we'll support an optional path argument to check for paths other than the current-working-directory. Arguments are processed via ArgumentParser and each command is automatically provided a parser to use. In addition to the parser each command is provided a few data attributes. Here is the **PinCommand** initializer:

    def __init__(self, args):
        self.cwd = os.getcwd()
        self.root = get_project_root(self.cwd)
        self.args = args
        self.parser = self._getparser()
        self.options = self._getoptions(args)

You can see that the command recieves the current-working-directory, the project root directory (if there is one), any arguments provided to the command and the ArgumentParser and the Options object returned by the parser. For the parser and options, PinCommand provides two methods that you can override in order to process your command's arguments. **PinCommand._getparser()** will call **PinCommand.setup_parser()**. Let's setup that path argument now:

    class CheckCommand(command.PinCommand):
        command = 'check'
    
        def setup_parser(self, parser):
            parser.add_argument('path', nargs='?', default=self.cwd)

That's all we have to do to add the optional path argument. Now, either the user supplied path or the current-working-directory will end up as an attribute; specifically **self.options.path**. We can use this data in the execute method to do our check.

    from pin.util import get_project_root

    class CheckCommand(command.PinCommand):
        command = 'check'
    
        def setup_parser(self, parser):
            parser.add_argument('path', nargs='?', default=self.cwd)

        def execute(self):
            root = get_project_root(self.options.path)
            if root:
                print "The path is a part of the project at:", root
            else:
                print "The path is not part of a pin project."

      

