## Quick Start Guide

This guide are for those who wish to get set up quickly with Intel HE Toolit.

In this guide, you will create a HE project, create custom build recipes, and
augment the toolit via plugins.

### HE toolkit installation

### Step 1:
Install the system dependencies for the toolkit: python >= 3.8, pip, git are met.

pre-commit tools for development, file can install dependencies with:
```bash
pip install -r <requirements-file>
```

### Step 2: Initialize hekit command using
```bash
git clone https://github.com/intel/he-toolkit.git
cd he-toolkit
./hekit init --default-config
```
### Running the docker build

### Step 1:
Common errors: First error is `Permission denied`. To mitigate the error,
ensure all users are added to the ‘docker’ user group. Other issue includes
system config error. Make sure ubuntu system time must be correct for the
physical location of the system. There are multiple proxy files that must be
set. Make sure to configure required proxy environment variables.
### Step 2: Install hekit docker build command below
```bash
hekit docker-build
```
### Step 2 (alternative): Using VS Code Server
 Allows users to interact with HE Toolkit via the VS Code IDE using following command
 ```bash
hekit docker-build --enable vscode
```
### How to create a custom recipe file and use it with hekit

Command for creating recipe file
```bash
hekit install recipes/default.toml
```
```bash
hekit build recipes/sample-kernels.toml
```
and
```bash
hekit build recipes/examples.toml
```
### Run one of the examples

### Step 1: Running on example
User can run many example commands by typing the command. For instance,
run_lr_example : will run the Logistic Regression example program.
run_query_example: This will run a Secure Query example allowing users to query
on a database of the 50 U.S. States.
run_sample_kernels_palisade: This will run several HE sample kernels in
PALISADE including Matrix Multiplication and Logistic Regression
run_psi_example: users to perform a set intersection between a user-defined
"client set" and a "server set.

### Create a new project with hekit
The command `new` can be used to create a new project.
```bash
hekit new example
```

### How to create plugins and subcommands for hekit

## Plugins sub-commands
```bash
hekit plugins list
```
| Sub-command | Description                       | Usage     |
|-------------|-----------------------------------|-----------|
| list        | Print the list of all plugins.    | hekit plugins list [--state {all,enabled,disabled}]
| install     | Install the plugin on the system. | hekit plugins install [--force] plugin-file
| remove      | Remove an installed plugin.       | hekit plugins remove [--all] [plugin-name]
| disable     | Disable an installed plugin.      | hekit plugins disable plugin-name
| enable      | Enable an installed plugin.       | hekit plugins enable plugin-name
| refresh     | Synchronize the information of the installed plugins. | hekit plugins refresh

### Creating a new plugin
The simplest version of a plugin must include a main directory that contains a
TOML file and at least one python file as shown in the following example

my-plugin
    |- __init__.py
    |- new-plugin.py
    |- plugin.toml
Note that it is recommended to have an __init__.py file as the plugins are
treated as python packages.

For delivering a plugin in zip or tarball format, a common file packaging
utility must be applied to the previous structure.

### TOML file
The TOML file must be named plugin.toml. It defines the settings of the plugin
such as name, version and entry point, as shown in the following example:

[plugin]
name = "my-plugin"
version = "1.1.0"
start = "new-plugin.py"

### Main directory
The plugin root directory must have the same name as the plugin, thus it must
be the same as the name value defined in the TOML file. This name must be a
unique label that will be used to identify the plugin in the system.
