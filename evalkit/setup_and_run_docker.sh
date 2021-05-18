#!/bin/bash

# Copyright (C) 2020-2021 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

set -e

echo -e "\nPLEASE READ ALL OF THE FOLLOWING INSTRUCTIONS:

The Following script will install docker, enable it to be run without administrative
privileges, and build/run a docker for testing several Homomophic Encryption workloads.

Do note that this script MUST BE RUN as a user BESIDES root. Also, if you
are located behind a firewall (corporate or otherwise), please make sure
you have the proxies setup accordingly (e.g. environment variables:
http_proxy and https_proxy). This script requires full internet connectivity.
Finally, this script may also prompt you for passwords required for installation.\n"

read -p "If understood, press enter to continue. Otherwise, exit with Ctrl+C"
echo

if [ "$EUID" -eq 0 ]
then
    echo -e "Error: Please run this script as non-root\n"
    exit
fi
if [ -n "$http_proxy" ] || [ -n "$https_proxy" ];
then
    PROXY=true
else
    PROXY=false
fi

echo -e "\nINSTALLING DOCKER FROM APT-GET..."
sudo apt-get update
sudo apt-get install -y containerd docker.io


if [ ! -d "/etc/systemd/system/docker.service.d" ] && [ "$PROXY" = true ];
then
    echo -e "\nCREATING DOCKER SERVICE DIRECTORY..."
    sudo mkdir -p /etc/systemd/system/docker.service.d
fi
if [ ! -f "/etc/systemd/system/docker.service.d/http-proxy.conf" ] && [ "$PROXY" = true ];
then
    echo -e "\nCREATING DOCKER PROXY CONFIG..."
    echo -e "[Service]
Environment=\"HTTP_PROXY=$http_proxy\"
Environment=\"HTTPS_PROXY=$http_proxy\"" | sudo tee /etc/systemd/system/docker.service.d/http-proxy.conf
    sudo systemctl daemon-reload

    echo -e "\nRESTARTING DOCKER SERVICE..."
    sudo systemctl restart docker
fi


if grep -q "docker" /etc/group
then
    echo -e "\ndocker group already exists...\n"
else
    sudo groupadd docker
fi

sudo gpasswd -a $USER docker
sudo chmod 666 /var/run/docker.sock

echo -e "\nCHECKING DOCKER FUNCTIONALITY..."
docker run hello-world

echo -e "\nCHECKING IN-DOCKER CONNECTIVITY..."
docker run -v $PWD/basic-docker-test.sh:/basic-docker-test.sh --env-file ./env.list ubuntu:bionic /bin/bash /basic-docker-test.sh

echo -e "\nBUILDING DOCKERFILE..."
docker build --build-arg http_proxy --build-arg https_proxy --build-arg socks_proxy --build-arg ftp_proxy --build-arg no_proxy --build-arg UID=$(id -u) --build-arg GID=$(id -g) --build-arg UNAME=$(whoami) -t ubuntu_he_test .
docker run -it ubuntu_he_test
