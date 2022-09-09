# Introduction to third party plugins
The `plugins` command can be used to integrate third party
plugins in the Intel HE Toolkit. However to be installed in
the system, the plugins must fulfill the expected format as
it is explained in section.

## Plugins commands
The option `-h` can be used to get details about the arguments
and usage of each command.

| Command | Description | Usage
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
the plugin in the system and disable its functionality, execute
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
that contains a toml file and at least one python file, as shown
in the following example

```
MyPlugin
    |- new-plugin.py
    |- plugin.toml
```

### Main directory
It must be named with an unique label that will be used to identify
the plugin in the system. This label must also used in a key-value
pair of the toml file.

### tmol file
This file with define the settings of the plugin as name, version
and entry point, as shown in the following example:
toml
```
[plugin]
name = "MyPlugin"
version = "1.1.0"
start = "new-plugin.py"
```

### Main python file
This file has the logic to start the execution of the functionality
provided by the plugin. However, in order to be integrated as an
valid element of the intel HE Toolkit, it is expected to used the
API argparse to define the arguments of the plugin.

Therefore, the file must have a function that its name must begin
and end with set_ and \_subparser, respectively. About its content,
it must define the arguments of the command as shown in the next example
```
def set_TBD_subparser(subparsers):
    """create the parser for the 'ACTION' plugin"""
    parser_TBD = subparsers.add_parser("ACTION", description="ADD-SUBPARSER-DESCRIPTION")
    parser_TBD.add_argument(
        "ARG1", description="ADD-ARG-DESCRIPTION"
    )
    parser_TBD.add_argument(
        "ARG2", description="ADD-ARG-DESCRIPTION"
    )
    parser_TBD.set_defaults(fn=NEW_FUNCTIONALITY)
```

The parameter `fn` of the function set_defaults must be set to the
function that implements the entry point of the functionality of the
plugin and uses the arguments defined in the previous step.
```
def NEW_FUNCTIONALITY(args) -> None:
    """Executes new functionality"""
    if(args.ARG1)
        pass
    elif(args.ARG2)
        pass
```
