## Introduction to `hekit`
The `hekit` tool can be used by the user to easily set up the required
environment to evaluate homomorphic encryption technology.

## Usage
`hekit` can be executed using the following options:
```
hekit [--config CONFIG_FILE] {init, list, install, build, fetch, remove}
```
where the options and input files are explained in the following sections.

### Flags

`-h, --help`: Shows the help message.

`--version`: Displays Intel HE toolkit version.

`--config CONFIG_FILE`: Use non-default [configuration
file](#configuration-file).  Default is `~/.hekit/default.config`.

`init`: Initializes hekit.

`list`: Lists installed components.

`install RECIPE_FILE`: Installs components defined in [recipe
file](#recipe-file).

`build RECIPE_FILE`: Builds components defined in [recipe file](#recipe-file).

`fetch RECIPE_FILE`: Fetches components defined in [recipe file](#recipe-file).

`remove component instance`: Uninstalls a specific component.

`--recipe_arg "key=value"`: Optional argument to replace data marked as !key!
in a [recipe file](#recipe-file).

### Configuration file

The configuration file defines the working directory where the libraries will
be available, for instance:
```
repo_location = "~/.hekit/components"
```
The toolkit provides [default.config](../default.config) file that can be used
as a valid option for --config argument.

### Recipe file

#### Simple example
The recipe file is a TOML file that defines the libraries and the required
actions to install them, as shown in the following example:
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
The [recipes](../recipes/) directory contains default recipes for setting up a
working environment.

#### Back substitution mechanism in recipe file
The value of the pair (key = "value") in the recipe file can be reused in other
sections of the file. This can be achieved using the following options:

%key% : back substitute a value from within the same instance.

$component/instance/key$ : back substitutes the `key` from a specific instance.

!key! : back substitute a value defined from an external source. If
`--recipe_arg` is not set, the user will be prompted to provide a value.

## Examples

Although optional, init command can be used to add hekit in the PATH variable
and enable the [tab completion](#tab-completion) feature.
The first time you run init you need to,
```bash
cd </he-toolkit/root/directory>
.\hekit init
```
Afterwards source your shell initialization file e.g. `~/.bashrc`. Now you can
run the `hekit` commands form anywhere.

In order to check the installed components, execute the list command
```bash
hekit list
```

The install command can be used to fetch, build, and install the required
libraries.
```bash
hekit install ../recipes/default.toml
```

Using fetch and build commands, the user has access to perform specific
actions. For example, for fetching libraries:
```bash
hekit fetch ../recipes/default.toml --recipe_arg "version=v1.2.3"
```

In order to uninstall a specific component, execute the remove command
```bash
hekit remove hexl 1.2.3
```

## Tab completion
As an optional feature, the user is able to enable tab completion feature using
[argcomplete](https://kislyuk.github.io/argcomplete/) library.

As described in its documentation, the following actions are required to
enable this functionality
- Install argcomplete:
```
pip install argcomplete
```

- If you have used `hekit init` command than you are set to go. Otherwise, if
  you would like to set it manually adding the following line in your shell
  initialization script e.g. .bashrc file.
```
eval "$(register-python-argcomplete hekit.py)"
```
