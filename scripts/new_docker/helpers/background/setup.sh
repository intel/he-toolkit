#!/bin/bash

# Copyright (C) 2020-2021 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

set -e

cd home/$(whoami)

# cmake
echo -e "\nINSTALLING CMAKE:"
wget https://github.com/Kitware/CMake/releases/download/v3.19.2/cmake-3.19.2-Linux-x86_64.sh
sudo chmod +x cmake-3.19.2-Linux-x86_64.sh
mkdir cmake_files
yes Y | ./cmake-3.19.2-Linux-x86_64.sh --skip-license --prefix=cmake_files
sudo cp -rf cmake_files/{doc,man,share} /
sudo cp -rf cmake_files/share /usr/
sudo cp -rf cmake_files/bin/* /bin/
rm -rf cmake_files
echo -e "DONE INSTALLING CMAKE\n"

# clang
echo -e "\nINSTALLING CLANG:"
sudo apt-get update
sudo apt-get -y install apt-transport-https
wget https://apt.llvm.org/llvm.sh
sudo chmod +x llvm.sh
sudo -E ./llvm.sh 10
echo -e "DONE INSTALLING CLANG\n"

# gcc-10
echo -e "\nINSTALLING GCC-10"
sudo add-apt-repository -y ppa:ubuntu-toolchain-r/test
sudo apt-get -y install gcc-10 g++-10
sudo update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-10 100 --slave /usr/bin/g++ g++ /usr/bin/g++-10 --slave /usr/bin/gcov gcov /usr/bin/gcov-10
echo -e "DONE INSTALLING GCC-10\n"

# Virtualenv
echo -e "\nINSTALLING VIRTUALENV"
sudo apt-get -y install python3-pip
sudo apt-get -y install python3-venv
python3 -m pip install --user virtualenv
echo -e "DONE INSTALLING VIRTUALENV\n"

# Last Dep
echo -e "\nINSTALLING AUTOCONF"
sudo apt-get install -y autoconf
echo -e "DONE INSTALLING AUTOCONF\n"

# Set git global proxy
git config --global http.proxy "$http_proxy"

# Unzip HE-Samples Source
echo -e "\nUNZIPPING HE-SAMPLES SOURCE"
tar -zxvf projects.tar.gz
pushd projects/he-samples
echo -e "DONE UNZIPPING\n"

# Build / Test he-toolkit
echo -e "\nCONFIGURING, BUILDING, & TESTING HE-SAMPLES:"
mkdir -p build && rm -rf ./build/*
pushd build

# ENABLE_[PALISADE|SEAL|INTEL_HEXL] are Enabled by Default
cmake .. -DENABLE_PALISADE=ON \
         -DENABLE_SEAL=ON \
         -DENABLE_INTEL_HEXL=ON \
         -DCMAKE_CXX_COMPILER=clang++-10 \
         -DCMAKE_C_COMPILER=clang-10 \
         -DCMAKE_BUILD_TYPE=Release
make -j
./sample-kernels/test/unit-test
echo -e "DONE TESTING HE-SAMPLES\n\n"
popd
popd
