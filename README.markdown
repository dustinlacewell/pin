pin
======

**pin** is a plugin-based command-line utility that helps you manage your software development projects. At it's core, it is a registry of where your projects reside on your file-system. Registering your project with **pin** lets you use utilize the various plugins. Since **pin** is generic, what this means exactly is based on what your project is and what plugins you have installed. 

### Installation 

    $ sudo pip install pin

### Usage

To use **pin** you will need to source it's shell-script which is installed under the name **pin.sh**. You may want to add this to your **~/.bashrc**:

    $ source pin.sh

The **pin** command will now be available to you. To see the core pin commands you can use the **help** command:

    $ pin help
    usage: pin [-v] subcommand
    
    positional arguments:
      subcommand     any subcommand available below
    
    optional arguments:
      -v, --version
    Available commands for /home/dlacewell:
    pin go [project]
      - Teleport to a specific project.
    pin help [-a] [command [subcommand]]
      -  This help information. 
    pin init
      - Initialize pin in the current directory.
    $ 


### Initialization
    
Lets try out **pin init** in a new directory:

    $ cd; mkdir tmp
    $ cd tmp/
    $ pin init
    Creating .pin directory structure...
    pin project initialized in: /home/dlacewell/tmp/
    $

**pin** has created a project directory located at */home/dlacewell/tmp/.pin/* **Generally, commands that operate upon your project can be used *anywhere* below the project's root directory**. You'll now notice that if we execute the help command once more the **init** command has been replaced by the **destroy** command. This feature of command relevancy is pretty handy. Depending on whether or not you're in a project or what kinds of tools (like fabric or paver) your project uses will affect what commands are available to you. 

    $ pin help
    usage: pin [-v] subcommand
    
    positional arguments:
      subcommand     any subcommand available below
    
    optional arguments:
      -v, --version
    Available commands for /home/dlacewell/tmp:
    pin destroy
      - Destroy and unregister the project from pin.
    pin go [project]
      - Teleport to a specific project.
    pin help [-a] [command [subcommand]]
      -  This help information. 

You can always pass the *-a* or *--all* option to help to see a list of all commands that **pin** knows about. However, do not expect irrelevant commands to do anything meaningful if you try to use them:
    
    $ pin help -a
    usage: pin [-v] subcommand
    
    positional arguments:
      subcommand     any subcommand available below
    
    optional arguments:
      -v, --version
    Available commands for /home/dlacewell/tmp:
    pin destroy
      - Destroy and unregister the project from pin.
    pin go [project]
      - Teleport to a specific project.
    pin help [-a] [command [subcommand]]
      -  This help information. 
    pin init [--venv] [--pip] [--autoenv]
      - Initialize pin in the current directory.

### Core Commands

**pin init** : Initializes the .pin directory and registers the path with ~/.pinconf/registry.yml

**pin destroy** : Deletes the project's .pin directory and unregisters the project path. Only works from inside a project tree.

**pin go <project-name>** : Teleports to the project root if a name is provided. If no name is provided a menu will be presented.

**pin help** : Lists all pin commands including any provided by installed plugins.

## Plugin Support

**pin** doesn't do much on it's own but plugins can add new functionality to existing commands or new commands all together. Let's go ahead and install the *pin-venv* plugins to give **pin** the ability to work with *VirtualEnv*.

Remove existing pin dot-folder and install pinvenv

    $ rm -fdr .pin/
    $ sudo pip install pinvenv
    ...

Notice that the init command now supports the --venv option

    $ pin help
    usage: pin [-v] subcommand
    
    positional arguments:
      subcommand     any subcommand available below
    
    optional arguments:
      -v, --version
    Available commands for /home/dlacewell/tmp:
    pin go [project]
      - Teleport to a specific project.
    pin help [-a] [command [command ...]]
      -  This help information. 
    pin init [--venv] [--autoenv]
      - Initialize pin in the current directory.


Reinitalize with VirtualEnv support

    $ pin init --venv
    Creating .pin directory structure...
    Creating virtualenv...
    pin project initialized in: /home/dlacewell/tmp
    $ ls .pin/env
    bin include lib
    $

### Get Plugins

Plugins to extend pin's core functionality can be found at the [Pin Cushion](https://github.com/dustinlacewell/pin/wiki/Pin-Cushion)

### Write Plugins

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

The base command class is **command.PinCommand**. Your command will be a subclass that you register with **command.register(cls)**. There are a number of methods that you can override to define the behavior of your command. At minimum your class needs to define a class-attribute '**command**' which is the name of your command. Let's write a simple command called '*check*' the determines if the current-working-directory is inside of a pin project:

    class CheckCommand(command.PinCommand):
        command = 'check'

Just to illustrate the proper way to handle arguments we'll support an optional path argument to check for paths other than the current-working-directory. Arguments are processed via an ArgumentParser and each command is automatically provided a parser to use. In addition to the parser each command is provided a few data attributes. Here is the **PinCommand** initializer method:

    def __init__(self, args):
        self.cwd = os.getcwd()
        self.root = get_project_root(self.cwd)
        self.args = args
        self.parser = self._getparser()
        self.options = self._getoptions(args)

You can see that the command recieves the current-working-directory, the project root directory (if there is one), any arguments provided to the command, the ArgumentParser and the Options object returned by the parser. For the parser and options, PinCommand provides the **PinCommand.setup_parser()** method that you can override in order to configure your command's arguments. Let's setup an optional path argument now:

    class CheckCommand(command.PinCommand):
        command = 'check'
    
        def setup_parser(self, parser):
            parser.add_argument('path', nargs='?', default=self.cwd)

That's all we have to do to add the optional path argument. Now, either the user supplied path or the current-working-directory will end up as an attribute; specifically **self.options.path**. We can use this data in the **PinCommand.execute()** method to do our check.

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

**get_project_root** takes a path and walks up through the parents checking for a **.pin** directory. If it finds it, it will return that path. This is how we know if we're under a project tree.      

### User Methods

In addition to **setup_parser** and **execute** there are a few other methods worth mentioning:

#### is_relevant

The **is_relevant** method is called for each command in various places such as the built in help command to determine what commands to show help for. That way the user is not encouraged, for example to attempt to reinitalize pin in an existing pin project or subdirectory of one (even though it wouldn't work anyway.) 

**is_relevant** returns True by default but you can use your own logic to determine if you command should be available:

    class PinInitCommand(command.PinCommand):
        '''Initialize pin in the current directory.'''
    
        command = 'init'
    
        def is_relevant(self):
            return not self.root

#### setup_parser

As mentioned above, **setup_parser** can be used to define the arguments for your command. If you've used ArgumentParser before you'll be comfortable adding arguments of various types. If not, you'll want to check the Argparse documentation. You can also use **setup_parser** to configure the parser in other ways, such as setting your command's usage or help. However setting the usage is discouraged as that will prevent any dynamically added arguments, from hooks, from appearing in your command's help. More on that later.

    class PinGoCommand(command.PinCommand):
        '''
        Teleport to a specific project.
        '''
        command = 'go'
    
        def setup_parser(self, parser):
            parser.add_argument('project', nargs="?")

#### write_script

The easiest way to explain the **write_script** method is with an example. The built in **`go'** command:

    class PinGoCommand(command.PinCommand):
        '''
        Teleport to a specific project.
        '''
        command = 'go'
    
        def setup_parser(self, parser):
            parser.add_argument('project', nargs="?")
    
        def execute(self):
            self.path = registry.pathfor(self.options.project)
            return self.path
    
        def write_script(self, file):
            if self.path:
                file.write("cd %s\n" % self.path)
            
    command.register(PinGoCommand)


The **PinGoCommand** takes a single optional argument **`project'**. When the command executes, it asks the **registry** module for the absolute path of the project containing the word the user supplied. **write_script** is run after the command has successfully executed. **PinGoCommand** uses the supplied **file** object to write a shell statement telling the user's shell to change directories to the previously looked up project path. Use **write_script** if you need to write a command that should affect the user's shell environment in this way.


#### execute

It should be fairly obvious that **execute** is where you should put the work of your command. One thing to mention though is that your command is only considered to have successfully executed if **execute** returns True. If you do not return a *truth-y* value, **done** and **write_script** will not be called.

    def execute(self):
        if self.root:
            self.raise_exists()
        else:
            print "Creating .pin directory structure..."
            registry.initialize_project(self.cwd)
            return True


#### done

**done**'s utility may be questionable but it is there. This method will only be called if your command's **execute** method returns a truthful value. So I guess it can be considered a conveinence for that condition.

    # from PinDestroyCommand
    def done(self):
        print "Pin project has been destroyed."


### Delegate Commands

**PinDelegateCommand** is a **PinCommand** that supports subcommands of various sorts. Delegate commands can also have functionality of their own. The subcommands can either be namespaced PinCommands or the subcommands can be dynamically interpreted depending on what you're trying to do. 

The basic **PinDelegateCommand** is one that comes with a number **namespaced PinCommands**. In the context of Pin, namespaced commands simply means that the **command name** is *prefixed* with the name of the parent command. Let's take a look at Pin's pip plugin, pin-pip.

    class PinPipCommand(command.PinDelegateCommand):
        '''
        Commands for managing dependencies with pip.
        '''
        command = 'pip'
        subcommands = [PinPipMeetCommand, PinPipRequiresCommand]
    
        def is_relevant(self):
            return self.root and \
                os.path.isfile(os.path.join(self.root, 'requirements.txt'))
    
        def setup_parser(self, parser):
            parser.usage = "pin pip [subcommand]"
        
    command.register(PinPipCommand)

**PinPipCommand** only implements two methods. The **is_relevant** method merely checks to see if there is a **requirements.txt** file in the project root. The **setup_parser** method simply hardcodes the command's usage string. You'll notice that there is a class attribute **subcommands** which lists two other classes. Let's take a look at **PinPipRequiresCommand**:

    class PinPipRequiresCommand(command.PinSubCommand):
        '''Print project's requirements.txt file'''
    
        command = 'pip-requires'
    
        def setup_parser(self, parser):
            parser.usage = "pin pip requires"
    
        def execute(self):
            self.script = ''
            requirements_file = os.path.join(self.root, 'requirements.txt')
            if os.path.isfile(requirements_file):
                self.script = "cat %s;" % requirements_file
                return True
            
        def write_script(self, file):
            file.write(self.script)

    command.register(PinPipRequiresCommand)

The **pip-requires** subcommand is also quite simple. The **setup_parser** method hardcodes the usage string. The **execute** method determines the project's **requirements.txt** file's absolute path and generates a one line shell script to **cat** out the contents of the file. Finally, the **write_script** method writes out the shell script into the file object resulting in the **requirements.txt** file to be displayed on the user's screen.

The important thing to note here is the name of the command, **pip-requires**. This is the namespacing bit we mentioned before. Namespacing the command in this way, by prefixing the name of the parent command, will ensure that **requires** is only available behind its parent, in this case **pip**.

    dlacewell@scarf:pin(master)$ pin requires
    usage: pin [-v] subcommand
    
    positional arguments:
      subcommand     any subcommand available below
    
    optional arguments:
      -v, --version
    Available commands for /home/dlacewell/dev/mine/pin:
    (...cont)


    dlacewell@scarf:pin(master)$ pin pip requires
    PyYAML>=3.09
    argparse>=1.2.1
    straight.plugin>=1.0


The raw name may also be used:

    dlacewell@scarf:pin(master)$ pin pip-requires
    PyYAML>=3.09
    argparse>=1.2.1
    straight.plugin>=1.0

To demonstrate delegate commands that dynamically interpret its subcommands, lets walk through Pin's Paver plugin pin-paver. If you're not familiar with Paver it is a commandline utility that allows you to easily invoke methods inside of your project's **pavement.py** file. These methods usually do work involving things like building documentation, packaging and things like that.

    class PinPaverCommand(command.PinDelegateCommand):
        '''Commands inside your pavement file.
        '''
        command = 'paver'
    
        def is_relevant(self):
            return self.root and \
                os.path.isfile(os.path.join(self.root, 'pavement.py'))

The **PinPaverCommand** starts off by defining its **is_relevant** method which only returns true if it can find a **pavement.py** file in the root of the Pin project.

        def setup_parser(self, parser):
            parser.usage = "pin paver [subcommand [args ..]]"
            parser.description = "Access commands within your pavement file"


The parser setup simply adds a dummy usage description to inform the user that the paver command takes subcommands. When we do **pin help paver** we see that the help includes the commands inside my **pavement.py** file:

    dlacewell@scarf:~/dev/mine/pin$ pin help paver
    usage: pin paver [subcommand [args ..]]
    
    Access commands within your pavement file
    
    positional arguments:
      subcommand
        sdist  - Generate docs and source distribution.

The way that **PinPaverCommand** informs Pin what subcommands are available it implements the **get_commands** method. **get_commands** returns a dictionary who's keys are the available commands. What values your dictionary keys map to isn't currently important as the values are unused. In the case of **PinPaverCommand**, this involves importing your **pavement.py** file and asking paver for a list of the tasks within:

        def get_subcommands(cls):
            cwd = os.getcwd()
            root = get_project_root(cwd)
            try:
                sys.path.append(root)
                mod = __import__('pavement')
                env = Environment(mod)
                tasks = env.get_tasks()
                maxlen, tasklist = _group_by_module(tasks)
                for name, group in tasklist:
                    if name == 'pavement':
                        return dict((t.shortname, t) for t in group)
            except ImportError, e:
                return dict()

Finally, to execute the specified paver command the paver module's regular api is used:

        def execute(self):
            if self.root:
                os.chdir(self.root)
                main(self.options.subcommand)
                return True

