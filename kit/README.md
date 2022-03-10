## Introduction
The hekit tool can be used by the user to easily set up the required environment to evaluate homomorphic encryption technology.

## Usage
The hekit can be executed using the following options:
```
cd kit
./hekit.py [--config CONFIG_FILE] {init, list, install, build, fetch, remove}
```
where the options and the input files are explained in the following sections.

### Flags

`-h, --help`: Shows the help message.

`--version`: Displays Intel HE toolkit version.

`--config CONFIG_FILE`: Defines a [configuration file](#configuration-file). Default is `~/.hekit/default.config`.

`init`: Initializes hekit.

`list`: Lists installed components.

`install RECIPE_FILE`: Installs components defined in [recipe file](#recipe-file).

`build RECIPE_FILE`: Builds components defined in [recipen file](#recipe-file).

`fetch RECIPE_FILE`: Fetches components defined in [recipen file](#recipe-file).

`remove component instance`: Uninstalls a specific component.

`--recipe_arg "key=value"`: Optional argument to replace data marked as !key! in a [recipen file](#recipe-file).

### Configuration file

The configuration file defines the working directory where the libraries will be available, for instance:
```
repo_location = "~/.hekit/components"
```
The toolkit provides [default.config](../default.config) file that can be used as a valid option for --config argument.

### Recipe File

The recipe File is a TOML file that defines the libraries and the required actions to install them, as shown in the following example:
```
[[library]]
skip = false
version = "!version!"
name = "v1.11.6"
init_fetch_dir = "fetch"
init_build_dir = "build"
init_install_dir = "build"
export_install_dir = "install"
fetch = "git clone https://gitlab.com/library/library-release.git --branch %name%"
pre-build = """cmake -S %init_fetch_dir%/library-release -B %init_build_dir%
               -DWITH_INTEL_HEXL=ON
               -DHEXL_DIR=$%hexl%/export_cmake$"""
build = "cmake --build %init_build_dir% -j"
post-build = ""
install = "cmake --install %init_install_dir%"
# Dependencies
hexl = "hexl/1.2.3"
```
The [recipes](../recipes/) directory contains the usual files to set up a working enviroment.

#### Back Sustitution in a recipe file
The specfic value of a pair (key = "value") in a recipe file can be reused in other sections of the file. That can be achieved using the following expressions:

%key% : it will be replaced with the string value of a key that was defined in the same section.

$key$ : similar as %key%, but it must be used when replacing dependecies.

!key! : it will be replaced with a string defined from an external source. If --recipe_arg is not set, there will be a prompt message asking about it.

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
./hekit.py --config ../default.config fetch ../recipes/default.toml --recipe_arg "version=v1.2.3"
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
