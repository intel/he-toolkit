# Copyright (C) 2021 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

##################################################
## Synthetic data generation for LR HE example
##################################################
find_package(Python3 COMPONENTS Interpreter Development)
if (Python3_VERSION VERSION_LESS 3.8)
  message(FATAL_ERROR "python >= 3.8 is required")
endif()

find_program(VIRTUALENV virtualenv)
if(VIRTUALENV)
    set(VIRTUALENV_PREFIX ${VIRTUALENV} -p python3)
else()
    set(VIRTUALENV_PREFIX ${Python3_EXECUTABLE} -m venv)
endif()

add_custom_command(
    OUTPUT venv
    COMMAND ${VIRTUALENV_PREFIX} venv
)

add_custom_command(
    OUTPUT venv.stamp
    DEPENDS venv requirements.txt
    COMMAND ${CMAKE_COMMAND} -E copy ${CMAKE_CURRENT_SOURCE_DIR}/requirements.txt ${CMAKE_CURRENT_BINARY_DIR}
    COMMAND ${CMAKE_COMMAND} -E copy ${CMAKE_CURRENT_SOURCE_DIR}/*.py ${CMAKE_CURRENT_BINARY_DIR}
    COMMAND ${CMAKE_COMMAND} -E copy ${CMAKE_CURRENT_SOURCE_DIR}/*.ipynb ${CMAKE_CURRENT_BINARY_DIR}
    COMMAND ${CMAKE_CURRENT_BINARY_DIR}/venv/bin/pip install -r requirements.txt --upgrade
    COMMAND touch venv.stamp
)

add_custom_command(
    OUTPUT gendata.stamp
    DEPENDS venv.stamp
    COMMAND ${CMAKE_CURRENT_BINARY_DIR}/venv/bin/python generate_data.py
    COMMAND touch gendata.stamp
)

add_custom_target(genSyntheticData
    DEPENDS gendata.stamp
)
