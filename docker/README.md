# Quick start

# Dependencies
This has been tested on Ubuntu 20.04
  Docker version 20.10.x

If you don't have docker in your system, here are the quick installation instructions
to install Docker from a standard Ubuntu Repository:
  https://linuxconfig.org/how-to-install-docker-on-ubuntu-20-04-lts-focal-fossa

Alternatively you can also install Docker from docker.com, See instructions at
  https://docs.docker.com/engine/install/ubuntu/


# Build
To build the base Ubuntu 20.04 image from whithin this directory
The arguments UNAME, UID, and GID need to be passed to the `docker build` command. There is no default set at the moment.

At the moment, there is no password set for the user `hexl`
```bash
docker build -f ./Dockerfile.UBUNTU.HEXL -t hetoolkit --build-arg UNAME=hexl --build-arg UID=3000 --build-arg GID=3000 .
```
Once the base docker image is created, you can start and log into the `hexl` user with the following command:
```bash
docker run --name hexl -h hexldemo -it hetoolkit /bin/bash
```
Everything going well you should a prompt into the toolkit
```
hexl@hexldemo:~$
```
