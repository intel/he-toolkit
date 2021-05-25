# Copyright (C) 2020-2021 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

# Pull base image.
FROM ubuntu:20.04

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

# Fix timezone configuration
ENV TZ=America/Vancouver
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Install.
RUN \
  sed -i 's/# \(.*multiverse$\)/\1/g' /etc/apt/sources.list && \
  apt-get update && \
  apt-get -y upgrade && \
  apt-get install -y build-essential && \
  apt-get install -y software-properties-common && \
  apt-get install -y byobu curl git htop man unzip vim wget sudo && \
  rm -rf /var/lib/apt/lists/*

# User-setup
ARG UNAME
ARG UID
ARG GID

ENV UNAME=$UNAME
RUN groupadd -g $GID $UNAME; exit 0
RUN useradd --no-log-init -m -u $UID -g $GID -s /bin/bash $UNAME

RUN echo "$UNAME ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers
RUN echo 'Defaults env_keep="https_proxy"' >> /etc/sudoers
RUN echo "Acquire::ftp::proxy \"$ftp_proxy\"; \n\
Acquire::socks::proxy \"$socks_proxy\"; \n\
Acquire::http::proxy \"$http_proxy\"; \n\
Acquire::https::Proxy \"$http_proxy\";" > /etc/apt/apt.conf

USER $UNAME

COPY projects.tar.gz /home/$UNAME/
COPY helpers.tar.gz /home/$UNAME/
RUN tar -zxvf /home/$UNAME/helpers.tar.gz --directory /home/$UNAME/
RUN sudo chmod +x /home/$UNAME/helpers/background/*
RUN sudo chmod +x /home/$UNAME/helpers/runner/*

# Define default command.
ENTRYPOINT "/home/$UNAME/helpers/background/setup.sh" && cd /home/$UNAME/helpers/runner && "/home/$UNAME/helpers/background/welcome_msg.sh" && /bin/bash
