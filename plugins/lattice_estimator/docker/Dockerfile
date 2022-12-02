# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

ARG sage_ver=9.7
FROM sagemath/sagemath:$sage_ver

ARG http_proxy
ARG https_proxy

ENV http_proxy=$http_proxy   \
    https_proxy=$https_proxy

USER root
RUN apt update && apt upgrade -y

RUN sage -pip install --proxy="${http_proxy}" \
           black                  \
           flake8                 \
           pyproject-flake8       \
           pytest                 \
           pytest-xdist           \
           nbmake                 \
           sphinx-book-theme      \
           sphinxcontrib-jupyter

WORKDIR /

CMD ["bash"]
