#!/bin/bash

set -e

http_proxy="$http_proxy"
https_proxy="$https_proxy"

echo -e "\nPLEASE READ ALL OF THE FOLLOWING INSTRUCTIONS:

The Following script will remove any pre-existing docker install,
install docker (docker.io and containerd), enable it to be run without
administrative privileges, configure the docker proxy (if applicable),
and modify the group settings/socket.

Do note that this script has a few usage requirements:
    1. This script MUST BE RUN as a user BESIDES root.
    2. If you are located behind a firewall (corporate or otherwise),
    please make sure you have the proxies setup accordingly
    (e.g. environment variables: http_proxy and https_proxy are set).
    3. Finally, this script may also prompt you for your sudo password
    required for installation or deletion.\n"

read -rp "If understood, press enter to continue. Otherwise, exit with Ctrl+C"
echo

if [ "$EUID" -eq 0 ]; then
  echo -e "Error: Please run this script as non-root\n"
  exit 1
fi

if [ -n "$http_proxy" ] || [ -n "$https_proxy" ]; then
  PROXY=true
else
  PROXY=false
fi

echo -e "\nREMOVING OLD DOCKER INSTALLATIONS..."
sudo apt-get purge -y docker*
sudo rm -rf /etc/docker*
sudo rm -rf /var/run/docker*
sudo rm -rf /etc/systemd/system/docker*
if grep -q docker /etc/group; then
  sudo groupdel docker
fi

echo -e "\nINSTALLING DOCKER FROM APT-GET..."
sudo apt-get update
sudo apt-get install -y containerd docker.io

if [ ! -d "/etc/systemd/system/docker.service.d" ] && [ "$PROXY" = true ]; then
  echo -e "\nCREATING DOCKER SERVICE DIRECTORY..."
  sudo mkdir -p /etc/systemd/system/docker.service.d
fi
if [ ! -f "/etc/systemd/system/docker.service.d/http-proxy.conf" ] && [ "$PROXY" = true ]; then
  echo -e "\nCREATING DOCKER PROXY CONFIG..."
  echo -e "[Service]
Environment=\"HTTP_PROXY=$http_proxy\"
Environment=\"HTTPS_PROXY=$http_proxy\"" | sudo tee /etc/systemd/system/docker.service.d/http-proxy.conf
  sudo systemctl daemon-reload

  echo -e "\nRESTARTING DOCKER SERVICE..."
  sudo systemctl reset-failed docker
  sudo systemctl restart docker
fi

if grep -q "docker" /etc/group; then
  echo -e "\ndocker group already exists...\n"
else
  sudo groupadd docker
fi

sudo gpasswd -a "$USER" docker
sudo chmod 666 /var/run/docker.sock

docker run hello-world

echo -e "\nDocker was installed successfully\n"
