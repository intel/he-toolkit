# Introduction to third party plugins
The `plugins` command can be used to integrate third party plugins
that expand the functionalities of the Intel HE Toolkit. Currently,
the program can install plugins stored in a directory or in a archive
file as zip or tarball file. A valid plugin must fulfill the expected
format as it is explained in section [Creating a new plugin](#creating-a-new-plugin).

## Plugins sub-commands
The option `-h` can be used to get details about the arguments
and usage of each sub-command.

| Sub-command | Description | Usage
|-----------|-----------|-----------|
| list | Print the list of all plugins. | hekit plugins list [--state {all,enabled,disabled}]
| install | Install the plugin in the system. | hekit plugins install [--force] plugin-file
| remove | Remove an installed plugin. | hekit plugins remove [--all] [plugin-name]
| disable | Disable an installed plugin. | hekit plugins disable plugin-name
| enable | Enable an installed plugin. | hekit plugins enable plugin-name

### Usage

#### list
In order to check all plugins in the system, execute the following command
```bash
hekit plugins list
```

Also, the argument `--state` can be used to filter the plugins
by state, for instance
```bash
hekit plugins list --state disabled
```

#### install
After downloading or creating a plugin, it can be installed in
the system executing the following command
```bash
hekit plugins install plugin-file
```

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

Besides, the argument `--all` can be used to remove all the
plugins that are present in the system.
```bash
hekit plugins remove --all
```

#### enable and disable
After installing a plugin, its default state is enabled. To keep
the plugin in the system but disabling its functionality, execute
the following command
```bash
hekit plugins disable plugin-name
```

In order to enable a plugin again, run the next command
```bash
hekit plugins enable plugin-name
```

## Creating a new plugin
The simplest version of a plugin must include a main directory
that contains a TMOL file and at least one python file, as shown
in the following example

```
MyPlugin
    |- new-plugin.py
    |- plugin.toml
```

For delivering a plugin in zip or tarball format, a common file
packaging utility must be applied to the previous structure.

### TMOL file
This file must be named as `plugin.toml`. It defines the settings
of the plugin as name, version and entry point, as shown in the
following example:
```bash
[plugin]
name = "MyPlugin"
version = "1.1.0"
start = "new-plugin.py"
```

### Main python file
This file has the logic to start the execution of the functionality
provided by the plugin, therefore its name must be equal to the value
of `start` defined in the TOML file.

In order to be integrated as an valid element of the intel HE Toolkit,
this file must have a function that its name must begin and end with
`set_` and `\_subparser`, respectively. About its content, it must define
the arguments of the command, using [API argparse](https://docs.python.org/3/library/argparse.html#),
as shown in the next example
```python
def set_TBD_subparser(subparsers):
    """create the parser for the TDB plugin"""
    parser_TBD = subparsers.add_parser("ACTION", description="ADD-SUBPARSER-DESCRIPTION")
    parser_TBD.add_argument(
        "ARG1", description="ADD-ARG-DESCRIPTION"
    )
    parser_TBD.add_argument(
        "ARG2", description="ADD-ARG-DESCRIPTION"
    )
    parser_TBD.set_defaults(fn=NEW_FUNCTIONALITY)
```

The parameter `fn` of the function `set_defaults` must be set to the
function that implements the entry point of the plugin, therefore, it
uses the arguments defined in the previous step.
```python
def NEW_FUNCTIONALITY(args) -> None:
    """Executes new functionality"""
    if(args.ARG1)
        pass
    elif(args.ARG2)
        pass
```

### Main directory
It must be named with the value of `name` defined in the TOML file.
This name must be an unique label that will be used to identify
the plugin in the system.
