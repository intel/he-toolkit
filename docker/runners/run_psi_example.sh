#!/bin/bash

# Copyright (C) 2020-2021 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

set -e

pushd "$HOME"/he-samples/build/examples/psi

echo "Do you want to create a file for storing the client set? (y/n)"
read createFile

if [ "$createFile" == "y" ]; then
  fileName=""
  isFlag=false
  for parameter in "$@"
  do
    if [ "$isFlag" = false ]; then
      if [[ "$parameter" == "-"* ]]; then
        isFlag=true
      else
        fileName=$parameter
        break
      fi
    else
      isFlag=false
    fi
  done

  if [ "$fileName" != "" ]; then
    echo "Writing $fileName file"
    sudo sh -c "> $fileName"

    newItem="y"
    while [ "$newItem" == "y" ]
    do
        echo "Enter a item of the client set"
        read itemVar
        sudo sh -c "echo $itemVar >> $fileName"

        echo "Do you want to enter other item? (y/n)"
        read newItem
    done
  fi
fi

echo "Executig the example"
OMP_NUM_THREADS="$(nproc)" ./psi "$@"

popd