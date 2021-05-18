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
sudo apt-get -y install gcc-9 g++-9 gcc-10 g++-10
sudo update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-10 100 --slave /usr/bin/g++ g++ /usr/bin/g++-10 --slave /usr/bin/gcov gcov /usr/bin/gcov-10
sudo update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-9 90 --slave /usr/bin/g++ g++ /usr/bin/g++-9 --slave /usr/bin/gcov gcov /usr/bin/gcov-9
echo -e "DONE INSTALLING GCC-10\n"

# Last Dep
echo -e "\nINSTALLING AUTOCONF"
sudo apt-get install -y autoconf
echo -e "DONE INSTALLING AUTOCONF\n"

# Unzip Source Code / Prebuilt Libs
echo -e "\nUNZIPPING SOURCE/LIBS:"
tar -zxvf projects.tar.gz
cd projects
echo -e "DONE UNZIPPING\n"

# Set git global proxy
git config --global http.proxy "$http_proxy"

# Build / Install Microsoft GSL
echo -e "\nBUILDING & INSTALLING GSL:"
git clone https://github.com/microsoft/GSL.git
pushd GSL
git checkout ef0ffefe
mkdir build && cd build
cmake .. -DCMAKE_INSTALL_PREFIX=../ \
         -DCMAKE_BUILD_TYPE=Release
make -j
make install
echo -e "DONE INSTALLING GSL\n"
popd

# Build / Test SEAL
echo -e "\nBUILDING & TESTING SEAL:"
pushd intel-seal
mkdir build && cd build
cmake .. -DSEAL_BUILD_DEPS=OFF \
         -DSEAL_USE_INTEL_HEXL=ON \
         -DSEAL_USE_MSGSL=ON \
         -DSEAL_USE_ZSTD=OFF \
         -DSEAL_USE_ZLIB=OFF \
         -DCMAKE_PREFIX_PATH=$(realpath ../../)/intel-hexl/lib/cmake\;$(realpath ../../)/GSL/share/cmake \
         -DCMAKE_INSTALL_PREFIX=../ \
         -DBUILD_SHARED_LIBS=OFF \
         -DCMAKE_C_COMPILER=clang-10 \
         -DCMAKE_CXX_COMPILER=clang++-10 \
         -DSEAL_BUILD_EXAMPLES=ON \
         -DCMAKE_CXX_FLAGS="-fvisibility=hidden -fvisibility-inlines-hidden" \
         -DCMAKE_BUILD_TYPE=Release
make -j
{ echo 7; echo 1; echo 3; echo 0; echo 0; } | ./bin/sealexamples && echo
make install
echo -e "DONE TESTING SEAL\n"
popd

# Build / Test Palisade
echo -e "\nBUILDING & TESTING PALISADE:"
pushd intel-palisade-development
git submodule sync --recursive
git submodule update --init  --recursive
mkdir build && cd build
cmake .. -DINTEL_HEXL_PREBUILT=ON \
         -DINTEL_HEXL_HINT_DIR=$(realpath ../../)/intel-hexl/lib/cmake/ \
         -DCMAKE_INSTALL_PREFIX=../ \
         -DBUILD_STATIC=ON \
         -DCMAKE_CXX_COMPILER=clang++-10 \
         -DCMAKE_C_COMPILER=clang-10 \
         -DCMAKE_BUILD_TYPE=Release
make -j
make testall
make install
echo -e "DONE TESTING PALISADE\n"
popd

# Build / Test he-toolkit
echo -e "\nBUILDING & TESTING HE-TOOLKIT:"
pushd he-toolkit
mkdir build && cd build
cmake .. -DENABLE_PALISADE=ON \
         -DPALISADE_PREBUILT=ON \
         -DPALISADE_HINT_DIR=$(realpath ../../)/intel-palisade-development/build \
         -DENABLE_SEAL=ON \
         -DSEAL_PREBUILT=ON \
         -DSEAL_HINT_DIR=$(realpath ../../)/intel-seal/build \
         -DCMAKE_PREFIX_PATH=$(realpath ../../)/intel-hexl/lib/cmake\;$(realpath ../../)/GSL/share/cmake \
         -DCMAKE_CXX_COMPILER=clang++-10 \
         -DCMAKE_C_COMPILER=clang-10 \
         -DCMAKE_BUILD_TYPE=Release
make -j
./sample-kernels/test/unit-test
echo -e "DONE TESTING HE-TOOLKIT\n\n"
popd
