#!/bin/bash

# Copyright (C) 2020-2021 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

set -e

echo "Running as user $USER..."

echo -e "\nTesting apt-get Config:"
echo "Acquire::ftp::proxy \"$ftp_proxy\"; \n\
Acquire::socks::proxy \"$socks_proxy\"; \n\
Acquire::http::proxy \"$http_proxy\"; \n\
Acquire::https::Proxy \"$http_proxy\";" > /etc/apt/apt.conf

echo -e "\nTesting apt-get:"
apt-get update && \
apt-get install -y build-essential wget

echo -e "\nTesting wget:"
wget http://www.google.com

echo -e "DONE"
