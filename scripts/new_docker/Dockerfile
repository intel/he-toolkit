# Copyright (C) 2020-2021 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

# Pull base image.
FROM ubuntu:20.04

LABEL maintainer="HE Toolkit Support <he_toolkit_support@intel.com>"

# Proxies, user configured
ARG http_proxy
ARG https_proxy
ARG socks_proxy
ARG ftp_proxy
ARG no_proxy

# User-setup
ARG UNAME
ARG UID
ARG GID

ENV http_proxy=$http_proxy   \
    https_proxy=$https_proxy \
    socks_proxy=$socks_proxy \
    ftp_proxy=$ftp_proxy     \
    no_proxy=$no_proxy       \
    DEBIAN_FRONTEND=noninteractive \
    TZ=UTC \
    UNAME=$UNAME

# Installation run as "root" in the container
# before switching to non-priviledged user for the toolkit.

RUN \
    # Initial setup \
    apt-get update && \
    apt-get install -y apt-utils && \
    apt-get install -y software-properties-common 
    # Basic Tools setup \
RUN apt-get -y dist-upgrade && \
    apt-get install -y libterm-readline-gnu-perl && \
    apt-get install -y --no-install-recommends tzdata && \
    apt-get install -y build-essential && \
    apt-get install -y byobu curl git htop man xz-utils unzip vim wget sudo cmake m4 file patchelf
    # Install and configure gcc 10 \
    # Add required PPA \
RUN add-apt-repository ppa:ubuntu-toolchain-r/ppa  && \
    apt-get install -y gcc-10 && \
    apt-get install -y g++-10 && \
    update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-9 10 && \
    update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-10 20 && \
    update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-10 20 && \
    update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-9 10 
    # Set timezone to UTC \
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
    echo $TZ > /etc/timezone && \
    dpkg-reconfigure --frontend noninteractive tzdata
    # Clean up \
RUN apt-get autoremove -y && \
    apt-get autoclean -y && \
    rm -rf /var/lib/apt/lists/*
    # User-setup \
RUN groupadd -g $GID $UNAME && \
    useradd --no-log-init -m -u $UID -g $GID -s /bin/bash $UNAME && \
    echo "$UNAME ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Switch user to
USER $UNAME

ENTRYPOINT cd /home/$UNAME && /bin/bash
