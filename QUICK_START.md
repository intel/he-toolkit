# Quick Start Guide

This guide are for those who wish to get set up quickly with Intel HE Toolit.

In this guide, you will get up and running with a VS Code enabled docker container.

## HE toolkit installation

### Step 1 Clone the repo
Make sure you have `git` on your system.
```bash
git clone https://github.com/intel/he-toolkit.git
```

### Step 2 Install the system dependencies for the toolkit 
Make sure your python >= 3.8 and that you have pip.

```bash
pip install -r requirements.txt
```

### Step 3: Initialize the `hekit` command
Move into your `he-toolkit` directory.
```bash
cd he-toolkit
```

For a default initialization of the toolkit, you will be asked
whether to modify your shell configuration file which you may wish to do yourself instead.
```bash
./hekit init --default-config
```


## Running the docker build

### Step 1 Sanity check
Check that `docker` is on your system. 

Moreover, check that you are in the `docker` group. You can use the `id` command to check. The
`docker` group should appear as one of your groups.


### Step 2 Using VS Code Server
For an IDE experience, we recommend building the VS Code enabled docker container.
 ```bash
hekit docker-build --enable vscode
```

### Step 3 Run your container


## Run an HE example program

### Step 1 View available compiled example programs

Through your browser, go to the terminal pane in VS Code and type,
```bash
welcome
```

A list of example programs will appear that can be run from the command line.
