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

`docker-build`: Builds the HE Toolkit Docker container. See [Docker
Build](../docker/README.md).

### Configuration file

The configuration file defines the working directory where the libraries will
be available, for instance:
```
repo_location = "~/.hekit/components"
```
The toolkit provides [default.config](../default.config) file that can be used
as a valid option for --config argument.

### Recipe file
The `hekit` tool relies on recipe files written in TOML to perform its `fetch`,
`build`, and `install` commands.

#### Simple example
The recipe file is a TOML file that defines the libraries and the required
actions to install them, as shown in the following example:
```
[[library]]
skip = false
version = "!version!"
name = "instance"
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
In the above example, the component name is `library` and the instance name is
`instance`, which must be unique. This will create a directory in
`~/.hekit/components` of the structure
`library/instance/{fetch,build,install}`.  This allows users to have multiple
instances of the same component on their system and to be able to link them in
a flexible manner.

The example library also has a dependency listed as `hexl = "hexl/1.2.3"` which
is used to back substitute the `export_cmake` value of that instance elsewhere
in the recipe file.

The [recipes](../recipes/) directory contains default recipes for setting up a
working environment.

#### Back substitution in recipe files
The value of the pair (key = "value") in the recipe file can be reused in other
sections of the file. This can be achieved using the following options for back
substitution

`%key%` : back substitute a value from within the same instance.

`$component/instance/key$` : back substitutes the `key` from a specific instance.

`!key!` : back substitute a value defined from an external source. If
`--recipe_arg` is not set, the user will be prompted to provide a value.

## Examples

Although optional, the `init` command can be used to add hekit to the `PATH`
variable and enable the [tab completion](#tab-completion) feature.
To initialize `hekit` for the first time run
```bash
cd <he-toolkit-root-directory>
./hekit init
```
Afterwards source your shell initialization file e.g. `~/.bashrc`. Now you can
run the `hekit` commands from anywhere.

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

The command new can be used to create a new application. When it is executed
with the option `-–based-on`, it will create a copy of the base project,
keeping its directory structure.
```bash
hekit new my-secure-query --based-on secure-query
```

However, when the command is executed without `-–based-on`.
```bash
hekit new example
```

It will create the following directory structure:
```bash
Projects
└── example
      |- CMakeLists.txt
      |- README.md
      └── include
            └── example.h
      └── recipes
            └── example.toml
      └── src
            └── example.cpp
```

And the following actions should be completed to build the new application:

* Open the toml file inside the recipes directory and replace `-DFLAG=TBD` with the required flags

* Open CMakeLists.txt and uncomment the statements for find_package and target_link_libraries of the required library. If other dependencies are needed, for instance Threads, the file must be updated to include and compile them.

* Add the code of the new application in the .cpp and .h files created by the command

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
