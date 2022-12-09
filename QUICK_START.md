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

Moreover, check that you are in the `docker` group. You can use the `id` to check. The
`docker` group should appear as one of your groups.


### Step 2 Using VS Code Server
For an IDE experience, we recommend building the VS Code enabled docker container.
 ```bash
hekit docker-build --enable vscode
```

## Run an HE example program

### Step 1: Running an example
Example programs can be run using the appropriate command. For instance,
run_lr_example : will run the Logistic Regression example program.
run_query_example: This will run a Secure Query example allowing users to query
on a database of the 50 U.S. States.
run_sample_kernels_palisade: This will run several HE sample kernels in
PALISADE including Matrix Multiplication and Logistic Regression
run_psi_example: users to perform a set intersection between a user-defined
"client set" and a "server set.

## Create a new project
The command `new` can be used to create a new project.
```bash
hekit new example
```
