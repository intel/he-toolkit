## Introduction
The kit tool is a collection of python scripts that can be used by the user to set-up easily the required environment to evaluate homomorphic encryption technology.

## Usage
The hekit can be executed using the following options:
```
cd kit
./hekit.py [--config CONFIG_FILE] {init, list, install, build, fetch, remove}
```
where the options are explained in the following section:

### Flags

`-h, --help`: Shows the help message.

`--version`: Displays Intel HE toolkit version.

`--config CONFIG_FILE`: Defines a configuration file. Default is `~/.hekit/default.config`.

`init`: Initializes hekit.

`list`: Lists installed components.

`install RECIPE_FILE`: Installs components defined in RECIPE_FILE.

`build RECIPE_FILE`: Builds components defined in RECIPE_FILE.

`fetch RECIPE_FILE`: Fetches components defined in RECIPE_FILE.

`remove component instance`: Uninstalls a specific component.

### Input Files

CONFIG_FILE file defines the working directory where the libraries will be available, for instance:
```
repo_location = "~/.hekit/components"
```
The toolkit provides a example of a CONFIG_FILE and it can be found at [default.config](../default.config).

RECIPE_FILE is a TOML file that defines the libraries and the required actions to install them. The default template can be found at [default.toml](../recipes/default.toml).

## Examples

Although optional, init command can be used to add hekit in the PATH variable and enable the [tab completion](#tab-completion) feature.
```bash
./hekit.py --config ../default.config init
```

In order to check the installed components, execute the list command
```bash
./hekit.py --config ../default.config list
```

The install command can be used to fetch, build and install the required libraries.
```bash
./hekit.py --config ../default.config install ../recipes/default.toml
```

Using fetch and build commands, the user has access to perform specific actions. For example, for fetching libraries:
```bash
./hekit.py --config ../default.config fetch ../recipes/default.toml
```

In order to uninstall a specific component, execute the remove command
```bash
./hekit.py --config ../default.config remove hexl 1.2.3
```

## Tab completion
As an optional feature, the user is able to enable tab completion feature using [argcomplete](https://kislyuk.github.io/argcomplete/) library.

As it is described in its documentation, the following actions are required to enable this functionality
- Install argcomplete:
```
pip install argcomplete
```

- Register the script explicitly adding the following line in e.g. .bashrc file. Please, be aware that this can be done by executing init command.
```
eval "$(register-python-argcomplete hekit.py)"
```
