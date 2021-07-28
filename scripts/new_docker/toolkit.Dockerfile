# Copyright (C) 2020-2021 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

# Username
ARG UNAME

FROM $UNAME/ubuntu_he_base:1.3

LABEL maintainer="HE Toolkit Support <he_toolkit_support@intel.com>"

COPY libs.tar.gz /

RUN tar -zxvf libs.tar.gz && \
    # Build and install SEAL \
    cd /SEAL && \
    cmake -S . -B build -DSEAL_USE_INTEL_HEXL=ON && \
    cmake --build build -j && \
    cmake --install build && \
    # Build and install PALISADE \
    cd /palisade-development && \
    cmake -S . -B build -DWITH_INTEL_HEXL=ON && \
    cmake --build build -j && \
    cmake --install build

# Build he-samples and link to SEAL and PALISADE
RUN mv /runners /home/$UNAME/ && \
    mv /he-samples /home/$UNAME/ && \
    cd /home/$UNAME/he-samples && \
    # FIXME: Temporarily disabling Palisade to get a working build \
    cmake -S . -B build \
             # -DENABLE_PALISADE=ON \
             -DENABLE_SEAL=ON \
    # FIXME: Setting HEXL to OFF as libraries include HEXL. Requires re-think \
             -DENABLE_INTEL_HEXL=OFF \
             -DCMAKE_CXX_COMPILER=clang++-10 \
             -DCMAKE_C_COMPILER=clang-10 \
             -DCMAKE_BUILD_TYPE=Release \
             # -DPALISADE_PREBUILT=ON \
             -DSEAL_PREBUILT=ON && \
    cmake --build build -j

# Switch user to
USER $UNAME

ENTRYPOINT cd /home/$UNAME/runners && \
           cat /home/$UNAME/welcome_msg.txt && \
           /bin/bash
