#!/bin/bash

# Copyright (C) 2021 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

#
# Checks and prints out to stdout where dependecies are located
# and return the number of dependecies not found.
# e.g. check_dependecies python nl cat
#
check_dependencies () {

  local not_found=0
  local dep=""

  for i in "$@"; do
    # type -P alternative to which. Which behaviour can vary based on platform.
    dep="$(type -P "$i")"
    # shellcheck disable=SC2181 # $dep gets used twice.
    if [ "$?" -eq 0 ]; then
      echo "Dependency '$i' in $dep"
    else
      echo "Dependency '$i' not found."
      not_found=$(( not_found + 1 ))
    fi
  done

  return "$not_found"

}

#
# Convert string to tuple (major, minor, patch)
#
__version_string_to_tuple() {

  # $1 is output tuple
  # $2 is input string
  local -r version_tuple=$( \
    sed -ne 's/[^0-9]*\([0-9x][0-9]*\)\.\([0-9x][0-9]*\)\.\([0-9x][0-9]*\).*/(\1 \2 \3)/p' \
    <<< "$2")

  eval "$1=$version_tuple"

}

#
# Check if version is what we require.
# e.g. check_required_command_version "python --version" "==3.5.0" # exact
# e.g. check_required_command_version "python --version" ">=3.5.0" # minimum
# e.g. check_required_command_version "python --version" ">=3.x.x" # minimum
#
check_required_command_version() {

  local -r version_cmd="$1"
  local version_policy="${2:0:2}" # First two chars
  local version_required="${2:2}" # The rest
  local actual_version

  # Only check version if command exists.
  if ! type -P "${version_cmd% *}" > /dev/null; then
    return 1
  fi

  __version_string_to_tuple actual_version "$($version_cmd)"
  __version_string_to_tuple version_required "$version_required"

  if [ "$version_policy" == "==" ]; then
    if [ "${actual_version[0]}" -eq "${version_required[0]}" ]; then
      if [ "${version_required[1]}" == "x" ]; then return 0; fi
      if [ "${actual_version[1]}" -eq "${version_required[1]}" ]; then
        if [ "${version_required[2]}" == "x" ]; then return 0; fi
        if [ "${actual_version[2]}" -eq "${version_required[2]}" ]; then
          return 0
        else
          return 1
        fi
      else
        return 1
      fi
    else
      return 1
    fi
  elif [ "$version_policy" == ">=" ]; then
    if [ "${actual_version[0]}" -ge "${version_required[0]}" ]; then
      if [ "${version_required[1]}" == "x" ]; then return 0; fi
      if [ "${actual_version[1]}" -ge "${version_required[1]}" ]; then
        if [ "${version_required[2]}" == "x" ]; then return 0; fi
        if [ "${actual_version[2]}" -ge "${version_required[2]}" ]; then
          return 0
        else
          return 1
        fi
      else
        return 1
      fi
    else
      return 1
    fi
  fi
}
