#!/bin/bash

# Copyright (C) 2020-2021 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

set -e

ftp_proxy="$ftp_proxy"
socks_proxy="$socks_proxy"
http_proxy="$http_proxy"
http_proxy="$http_proxy"

echo "Running as user $USER..."

echo -e "\nTesting apt-get Config:"
cat > /etc/apt/apt.conf << EOF
Acquire::ftp::proxy "$ftp_proxy";
Acquire::socks::proxy "$socks_proxy";
Acquire::http::proxy "$http_proxy";
Acquire::https::proxy "$http_proxy";
EOF

cat /etc/apt/apt.conf

echo -e "\nTesting apt-get:"
apt-get update \
  && apt-get install -y build-essential wget

echo -e "\nTesting wget:"
wget http://www.google.com

echo "DONE"
