# Copyright (C) 2020-2021 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

LABEL maintainer="HE Toolkit Support <he_toolkit_support@intel.com>"

# Pull base image.
FROM ubuntu:20.04

#Set-up Proxies, is user configured.
# Proxies
ARG http_proxy
ARG https_proxy
ARG socks_proxy
ARG ftp_proxy
ARG no_proxy

ENV http_proxy=$http_proxy
ENV https_proxy=$https_proxy
ENV socks_proxy=$socks_proxy
ENV ftp_proxy=$ftp_proxy
ENV no_proxy=$no_proxy

#For the rest of the installation run as "root" in the container
#before switching to non-priviledged user for the toolkit.

USER root

# Initial setup
Run DEBIAN_FRONTEND=noninteractive \
  apt-get update && \
  apt-get install -y apt-utils&& \
  apt-get install -y software-properties-common
# Basic Tools setup
Run DEBIAN_FRONTEND=noninteractive \
  apt-get -y dist-upgrade && \
  apt-get install -y libterm-readline-gnu-perl && \
  apt-get install -y --no-install-recommends tzdata && \
  apt-get install -y build-essential && \
  apt-get install -y byobu curl git htop man xz-utils unzip vim wget sudo cmake m4 file patchelf

# Install and configure gcc 10
# Add required PPA
RUN add-apt-repository ppa:ubuntu-toolchain-r/ppa  
Run DEBIAN_FRONTEND=noninteractive \
  apt-get install -y gcc-10 && \
  apt-get install -y g++-10 && \
  update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-9 10 && \
  update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-10 20 && \
  update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-10 20 && \
  update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-9 10 
  
# Set timezone to UTC
ENV TZ=UTC
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN dpkg-reconfigure --frontend noninteractive tzdata

# Clean up
Run DEBIAN_FRONTEND=noninteractive \
  apt-get autoremove -y && \
  apt-get autoclean -y && \
  rm -rf /var/lib/apt/lists/*
   
# User-setup
ARG UNAME
ARG UID
ARG GID

ENV UNAME=$UNAME
RUN groupadd -g $GID $UNAME; exit 0
RUN useradd --no-log-init -m -u $UID -g $GID -s /bin/bash $UNAME
RUN echo "$UNAME ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

USER $UNAME

ENTRYPOINT cd /home/$UNAME && /bin/bash
