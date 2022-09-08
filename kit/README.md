# Introduction to `hekit`
The `hekit` tool can be used by the user to easily set up the required
environment to evaluate homomorphic encryption technology.

## Contents

- [Introduction to hekit](#introduction-to-hekit)
  - [Global Options](#global-options)
  - [Commands](#commands)
    - [Configuration file](#configuration-file)
    - [Recipe file](#recipe-file)
      - [Simple example](#simple-example)
      - [Back substitution in recipe files](#back-substitution-in-recipe-files)
  - [Examples](#examples)
     - [init](#init)
     - [list](#list)
     - [fetch, build and install](#fetch-build-and-install)
     - [remove](#remove)
     - [check-dependencies](#check-dependencies)
     - [new](#new)
  - [Tab completion](#tab-completion) 

## Global Options

`-h, --help`: Shows the help message.

`--version`: Displays Intel HE toolkit version.

## Commands
The option `-h` can be used to get details about the arguments and usage of each command.

| Command | Description | Usage
|-----------|-----------|-----------|
| init | Initializes hekit. | hekit init [--default-config]
| list | Lists installed components. |  hekit [--config CONFIG_FILE] list 
| install | Installs components defined in [recipe file](#recipe-file). | hekit install [--config CONFIG_FILE] [--recipe_arg RECIPE_ARG] [-f] recipe-file
| build | Builds components defined in [recipe file](#recipe-file). | hekit build [--config CONFIG_FILE] [--recipe_arg RECIPE_ARG] [-f] recipe-file
| fetch | Fetches components defined in [recipe file](#recipe-file) | hekit fetch [--config CONFIG_FILE] [--recipe_arg RECIPE_ARG] recipe-file
| remove | Uninstalls instances or components. | hekit remove [--config CONFIG_FILE] [--all] [component] [instance]
| check-dependencies | Checks system dependencies. | hekit check-dependencies dependencies-file
| new | Create a new project. | hekit new [--directory DIRECTORY] [--based-on {logistic-regression,psi,secure-query}] name|
| plugins | Handle third party plugins. | hekit plugins {list,install,remove,enable,disable}
| docker-build | Builds the HE Toolkit Docker container. See [Docker Build](../docker/README.md). | hekit docker-build [--id ID] [--clean] [--check-only] [--enable {vscode}]
| gen-primes | Generates primes in range [n, m] where n, m are positive integers. See [Tools](./tools/README.md). | hekit gen-primes start stop
| algebras  | Generates ZZ_p[x]/phi(X) algebras. . See [Tools](./tools/README.md). | hekit algebras [-p P] [-d D] [--no-corrected] [--no-header]

### Configuration file

The configuration file defines the working directory where the libraries will
be available, for instance:
```
repo_location = "~/.hekit/components"
```
The comamnds `list`, `fetch`, `build`, `install` and `remove` uses a 
default configuration file located in `~/.hekit/default.config`. However, the argument 
`--config CONFIG_FILE` can be used to define the location of non-default configuration file

The toolkit provides [default.config](../default.config) file that can be used
as template and it is a valid option for `--config` argument.

### Recipe file
The `hekit` tool relies on recipe files written in TOML to perform its `fetch`,
`build`, and `install` commands.

#### Simple example
The recipe file is a TOML file that defines the libraries and the required
actions to install them, as shown in the following example:
```
[[library]]
skip = false
version = "5.2.1"
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

### init
Although optional, the `init` command can be used to add hekit to the `PATH`
variable and enable the [tab completion](#tab-completion) feature.
To initialize `hekit` for the first time run
```bash
cd <he-toolkit-root-directory>
./hekit init
```
Afterwards source your shell initialization file e.g. `~/.bashrc`. Now you can
run the `hekit` commands from anywhere.

Also, the `init` command can be executed with `--default-config` flag. This
will create a directory `~/.hekit` in the user's home directory and create the
`default.config`.  This directory will be where all components built and
installed by `hekit` will be kept.
```bash
cd <he-toolkit-root-directory>
./hekit init --default-config
```

### list
In order to check the installed components, execute the following command
```bash
hekit list
```

### fetch, build and install
The `install` command can be used to fetch, build, and install the required
libraries.
```bash
hekit install ./recipes/default.toml
```

Using `fetch` and `build` commands, the user has access to perform specific
actions. For example, for fetching libraries
```bash
hekit fetch ./recipes/examples.toml --recipe_arg "toolkit-path=~/he-toolkit"
```

By default, if actions as build or install were executed successfully,
the next time that the command is executed, they are going to be skipped.
For re-executing actions such as build or install, the flag `--force` must be
set.
```bash
hekit build ./recipes/examples.toml --force
```

### remove
In order to uninstall a specific instance, execute the `remove` command with the component and instance name
```bash
hekit remove hexl 1.2.3
```

For uninstalling all the instances of a component, execute the `remove` command with only the component name
```bash
hekit remove hexl
```

Also, to uninstall all components, use the following command
```bash
hekit remove --all
```

### check-dependencies
To check system dependencies, execute
```bash
hekit check-dependencies dependencies.txt
```

### new
The command `new` can be used to create a new project. When it is executed
with the option `-–based-on`, it will create a copy of the base project,
keeping its directory structure.
```bash
hekit new my-secure-query --based-on secure-query
```

However, when the command is executed without `-–based-on`
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

The following actions should be completed to build the new project:

* Open the `toml` file inside the recipes directory and replace `-DFLAG=TBD`
  with the desired CMake flags for your project.

* Open `CMakeLists.txt` and uncomment the statements for `find_package` and
  `target_link_libraries` of the required library. If other dependencies are
  needed, for instance `Threads`, the file must be updated to include and
  compile them.

* Add and/or write the code of the new project in the `.cpp` and `.h` files
  created by the command.

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
  initialization script e.g. `.bashrc` file.
  ```
  eval "$(register-python-argcomplete hekit.py)"
  ```
