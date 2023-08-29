# Quick Start Guide

This guide is for those who wish to get set up quickly with Intel HE Toolkit.

In this guide, you will get up and running with a VS Code enabled docker
container.

## HE Toolkit installation

### Step 1 Clone the repo
Make sure you have `git` on your system.
```bash
git clone https://github.com/intel/he-toolkit.git
```

### Step 2 Install the system dependencies for the toolkit
Move into your `he-toolkit` directory.
```bash
cd he-toolkit
```

Make sure your python >= 3.10 and that you have pip.
```bash
python --version
pip install -r requirements.txt
```

### Step 3: Initialize the `hekit` command
For a default initialization of the toolkit, you will be asked whether to
modify your shell configuration file which you may wish to do yourself instead.
```bash
./hekit init --default-config
```

## Running the docker build

### Step 1 Sanity check
Check that the `docker` command is on your system.

Moreover, check that you are in the `docker` group. You can use the `id`
command to check. The `docker` group should appear as one of your groups.

### Step 2 Using VS Code Server
For an IDE experience, we recommend building the VS Code enabled docker
container.
 ```bash
hekit docker-build --enable vscode
```

### Step 3 Run your container
To run the container run
```bash
docker run -d -p <ip addr>:<port>:8888 <username>/ubuntu_he_vscode:<hekit-version>
```
Note if you do not specify an IP address, it will default to `localhost`
(0.0.0.0).

### Step 4 Connect to the VSCode IDE through the browser
Using the browser of your choice, navigate to `<ip addr>:<port>`. eg.,
`localhost:1234`.

If you cannot remember what IP/port was assigned to the docker container, run
```bash
docker ps
```
to list the current running containers and it should list the IP/port used by
your container.

## Run an HE example program

### Step 1 View available compiled example programs
Through your browser, go to the terminal pane in VS Code and type,
```bash
source ~/he-toolkit/docker/runners.sh
```
This will provide access to a list of example programs that can be run from the
command line.

To view the list of programs run
```bash
welcome_message
```
