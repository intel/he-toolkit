# Introduction to third party plugins
The `plugins` command can be used to integrate third party plugins
that expand the functionalities of Intel HE Toolkit. However,
to be installed on the system, the plugins must fulfill the expected
format as explained in section [Creating a new plugin](#creating-a-new-plugin).


## Contents
- [Introduction to third party plugins](#introduction-to-third-party-plugins)
  - [Plugins sub-commands](#plugins-sub-commands)
  - [Usage](#usage)
     - [list](#list)
     - [install](#install)
     - [remove](#remove)
     - [enable and disable](#enable-and-disable)
     - [refresh](#refresh)
  - [Creating a new plugin](#creating-a-new-plugin)
     - [TOML file](#toml-file)
     - [Main python file](#main-python-file)
     - [Main directory](#main-directory)

## Plugins sub-commands
The option `-h` can be used to get details about the arguments
and usage of each sub-command.

| Sub-command | Description | Usage
|-----------|-----------|-----------|
| list | Print the list of all plugins. | hekit plugins list [--state {all,enabled,disabled}]
| install | Install the plugin on the system. | hekit plugins install [--force] plugin-file
| remove | Remove an installed plugin. | hekit plugins remove [--all] [plugin-name]
| disable | Disable an installed plugin. | hekit plugins disable plugin-name
| enable | Enable an installed plugin. | hekit plugins enable plugin-name
| refresh | Synchronize the information of the installed plugins. | hekit plugins refresh

### Usage

#### list
In order to check all plugins on the system, execute the following command
```bash
hekit plugins list
```

Moreover, the argument `--state` can be used to filter the plugins
by state {enabled, disabled}, for instance
```bash
hekit plugins list --state disabled
```

#### install
After downloading or creating a plugin, it can be installed on
the system through executing the following command
```bash
hekit plugins install plugin-file
```
The `plugin-file` can be a directory, a zip file, or a tarball file.
Python understands most compression schemes used for tarballs. Both
tarballs and zip files can optionally contain more than one plugin
directory.

Additionally, the argument `--force` can be used to update the
version without further interaction.
```bash
hekit plugins install plugin-file --force
```

#### remove
In order to remove a specific plugin, execute the following command
```bash
hekit plugins remove plugin-name
```

The argument `--all` can be used to remove all plugins that are present on the
system.
```bash
hekit plugins remove --all
```

#### enable and disable
After installing a plugin, its default state is enabled. To keep
the plugin on the system with its functionality disabled, execute
the following command
```bash
hekit plugins disable plugin-name
```

In order to enable a plugin again, run the command
```bash
hekit plugins enable plugin-name
```

#### refresh
Execute the following command to synchronize the information in plugin
config file with the plugins located on `~/.hekit/plugins`
```bash
hekit plugins refresh
```

## Creating a new plugin
The simplest version of a plugin must include a main directory
that contains a TOML file and at least one python file, as shown
in the following example
```
my-plugin
    |- new-plugin.py
    |- plugin.toml
```

For delivering a plugin in zip or tarball format, a common file
packaging utility must be applied to the previous structure.

### TOML file
The TOML file must be named `plugin.toml`. It defines the settings
of the plugin such as name, version and entry point, as shown in the
following example:
```bash
[plugin]
name = "my-plugin"
version = "1.1.0"
start = "new-plugin.py"
```

### Main python file
The main python file contains the logic to start the execution of the
functionality provided by the plugin, therefore the filename must be
the same as the value of `start` defined in the TOML file.

In order to be integrated as a valid component of Intel HE Toolkit,
the file must have a function with a name that must begin and end with `set_`
and `_subparser`, respectively. This python function must define the
arguments of the command using python's
[argparse API](https://docs.python.org/3/library/argparse.html#) as shown in
the following example template
```python
def set_TBD_subparser(subparsers):
    """create the parser for the TDB plugin"""
    parser_TBD = subparsers.add_parser("my-plugin", description="ADD-SUBPARSER-DESCRIPTION")
    parser_TBD.add_argument("ARG1", description="ADD-ARG-DESCRIPTION")
    parser_TBD.add_argument("ARG2", description="ADD-ARG-DESCRIPTION")
    parser_TBD.set_defaults(fn=ADD_NEW_FUNCTIONALITY)
```

In the previous code, the following conditions must be met:

* The value of the first paramenter of `subparsers.add_parse` must be the
same as the value of `start` defined in the TOML file.

* `ADD_NEW_FUNCTIONALITY` (parameter `fn` of `set_defaults`) is the function
that implements the entry point of the plugin. Therefore, this function
must use the plugin's arguments, for instance:
```python
def ADD_NEW_FUNCTIONALITY(args) -> None:
    """Executes new functionality"""
    if(args.ARG1)
        # logic for ARG1
        ...
    if(args.ARG2)
        # logic for ARG2
        ...
```

### Main directory
The plugin root directory must have the same name as the plugin, thus
it must be the same as the `name` value defined in the TOML file. This
name must be a unique label that will be used to identify the plugin
in the system.
