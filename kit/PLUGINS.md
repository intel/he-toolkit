# Introduction to `plugins` command
The `plugins` command can be used by the user to integrate
third party plugins in the Intel HE toolkit.

## Commands
The option `-h` can be used to get details about the arguments
and usage of each command.

| Command | Description | Usage
|-----------|-----------|-----------|
| list | Print the list of all plugins. | hekit plugins list [--state {all,enabled,disabled}]
| install | Install the plugin in the system. | hekit plugins install [--force] plugin-file
| remove | Remove an installed plugin. | hekit plugins remove [--all] [plugin-name]
| disable | Disable an installed plugin. | hekit plugins disable plugin-name
| enable | Enable an installed plugin. | hekit plugins enable plugin-name

## Usage

### list
In order to check the installed plugins, execute the following command
```bash
hekit plugins list
```

Also, the argument `--state` can be used to filter the plugins
by state, for instance
```bash
hekit plugins list --state disabled
```

### install
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

### remove
In order to check the remove a specific plugin, execute the
following command
```bash
hekit plugins remove plugin-name
```

Besides, the argument `--all` can be used to remove all the
plugins present in the system.
```bash
hekit plugins remove --all
```

### enable and disable
After installing a plugin, its defaault state is enable. When
the user wants to keep the plugin in the system and disable its
functionality, execute the following command
```bash
hekit plugins disable plugin-name
```

To enable a plugin again, run the next command
```bash
hekit plugins enable plugin-name
```
