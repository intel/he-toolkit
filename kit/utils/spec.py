# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

"""This module handles the specification file a.k.a. recipe"""

from __future__ import annotations

from re import findall
from dataclasses import dataclass
from typing import Dict
from toml import dump, load
from kit.utils.tsort import tsort  # pylint: disable=no-name-in-module
from kit.utils.typing import PathType

RecipeArgDict = Dict[str, str]


def read_spec(component, instance, repo_location):
    """Return hekit.spec file as a dict"""
    path = f"{repo_location}/{component}/{instance}/hekit.spec"
    spec = load(path)
    # There should only be one instance
    return spec[component][0]


def fill_user_string_dict(d, recipe_arg_dict: RecipeArgDict):
    """Returns a dict with str values written by the user.
    NB. Only works for flat str value dict."""

    def fill_user_str(s):
        """s can be a string or a list of strings"""
        if isinstance(s, str):
            symbols = findall(r"(!(.*?)!)", s)
            if not symbols:
                return s

            new_s = s
            for symbol, k in symbols:
                try:
                    value = recipe_arg_dict[k]
                except KeyError:
                    value = input(f"Please enter {k}: ")
                    # Save current value in case the same key
                    # is needed in other place
                    recipe_arg_dict[k] = value

                new_s = new_s.replace(symbol, value)

            return new_s

        if isinstance(s, list):
            return [fill_user_str(e) for e in s]

        # Not str or list
        return s

    return {k: fill_user_str(v) for k, v in d.items()}


def fill_self_ref_string_dict(d, repo_path):
    """Returns a dict with str values.
    NB. Only works for flat str value dict."""

    def fill_str(s):
        """s can be a string or a list of strings"""
        if isinstance(s, str):
            symbols = findall(r"(%(.*?)%)", s)
            if not symbols:
                return s

            new_s = s
            for symbol, k in symbols:
                new_s = new_s.replace(symbol, fill_str(d[k]))

            return new_s

        if isinstance(s, list):
            return [fill_str(e) for e in s]

        # Not str or list
        return s

    def fill_dep_str(s):
        """s can be a string or a list of strings"""
        if isinstance(s, str):
            symbols = findall(r"(\$(.*?)/(.*?)/(.*?)\$)", s)
            if not symbols:
                return s

            new_s = s
            for symbol, comp, name, k in symbols:
                # Assume finalized spec is already expanded
                # The dependency has already been installed
                sub = read_spec(comp, name, repo_path)
                new_s = new_s.replace(symbol, sub[k])

            return new_s

        if isinstance(s, list):
            return [fill_dep_str(e) for e in s]

        # Not str or list
        return s

    return {k: fill_dep_str(fill_str(v)) for k, v in d.items()}


def fill_dependencies(d):
    """ Returns a list of dependencies defined
    and used in the recipe file """
    dependency_list = []

    def get_dependencies(s):
        """s can be a string or a list of strings"""
        if isinstance(s, str):
            symbols = findall(r"(\$%(.*?)%/.*\$)", s)
            if not symbols:
                return

            for _, k in symbols:
                # Assume dependecies are define as:
                # name/version
                dependency, _ = d[k].split("/")
                dependency_list.append(dependency)

        elif isinstance(s, list):
            for e in s:
                get_dependencies(e)

    for v in d.values():
        get_dependencies(v)

    return dependency_list


def fill_rloc_paths(d, repo_location):
    """Create absolute path for the top-level attribs that begin
       with 'init_' or '_export_' by prepending repo location"""
    for k, v in d.items():
        if k.startswith("init_") or k.startswith("export_"):
            d[k] = f"{repo_location}/{v}"
    return d


class InvalidSpecError(Exception):
    """InvalidSpecError exception raised for an invalid spec"""


@dataclass(frozen=True)
class Spec:
    """hekit component specification"""

    component: str
    _instance_spec: dict
    repo_location: str

    # Keys will act as property methods
    # Values will be used as defaults in Spec obj creation
    _fixed_attribs = {
        "name": "",
        "skip": False,
        # Stages
        "pre_fetch": "",
        "fetch": "",
        "post_fetch": "",
        "pre_build": "",
        "build": "",
        "post_build": "",
        "pre_install": "",
        "install": "",
        "post_install": "",
        # Inittializer directories
        "init_fetch_dir": "fetch",
        "init_build_dir": "build",
        # This one is counter-intuitive
        "init_install_dir": "build",
    }

    recipe_arg_dict = {}

    # Factory from TOML file
    @classmethod
    def from_toml_file(
        cls, filename: PathType, rloc: PathType, recipe_arg_dict: RecipeArgDict
    ):
        """Generator yield Spec objects.
        Process spec file: perform substitutions and expand paths."""

        # Dictionary filled with recipe_arg values
        cls.recipe_arg_dict = recipe_arg_dict

        # load the recipe file
        toml_specs = load(filename)

        # create dependency graph
        dependency_dict = {
            component: fill_dependencies(instance_spec)
            for component, instance_specs in toml_specs.items()
            for instance_spec in instance_specs
        }

        # apply topological sorting
        sorted_components = tsort(dependency_dict)

        # create specs
        for component in sorted_components:
            for instance_spec in toml_specs[component]:
                yield cls.from_instance_spec(component, instance_spec, rloc)

    @staticmethod
    def _expand_instance(component: str, instance: dict, rloc: str):
        """Expansion operations"""
        # substitution from user must come before rloc expansion
        # to avoid asking for the same data several times
        instance = fill_user_string_dict(instance, Spec.recipe_arg_dict)
        if rloc != "":
            instance_name = instance["name"]
            instance = fill_rloc_paths(instance, f"{rloc}/{component}/{instance_name}")
        # Substitution must come after rloc expansion
        instance = fill_self_ref_string_dict(instance, rloc)
        return instance

    @classmethod
    def _validate_instance(cls, instance: dict) -> None:
        """Validates the instance.
        This method is gnostic about the spec"""

        # Name attrib must be provided
        if "name" not in instance.keys():
            raise InvalidSpecError("'name' was not provided for instance")

        if not isinstance(instance.get("skip", False), bool):
            raise InvalidSpecError("'skip' not of type bool")

        do_not_include = {"skip"}
        for attrib in cls._fixed_attribs.keys() - do_not_include:
            for_test = instance.get(attrib, str())
            if not isinstance(for_test, str):
                raise InvalidSpecError(f"'{attrib}' is not a string")

    @staticmethod
    def _validate_unique_instance(component: str, instance: dict, rloc: str) -> None:
        # load previous spec from info file
        try:
            instance_name = instance["name"]
            previous_instance = read_spec(component, instance_name, rloc)
            if previous_instance != instance:
                raise InvalidSpecError(
                    f"{component}/{instance_name} is already present but it was executed with different options"
                )
        except FileNotFoundError:
            pass

    # Factory given parsed TOML python dict
    @classmethod
    def from_instance_spec(cls, component: str, instance_spec: dict, rloc: str) -> Spec:
        """Expand paths.
        Populate the fixed attribs and place others in dictionary."""
        cls._validate_instance(instance_spec)
        # Add some defaults and override with input instance spec
        instance_spec_with_defaults = {**cls._fixed_attribs, **instance_spec}
        expanded_instance_spec = cls._expand_instance(
            component, instance_spec_with_defaults, rloc
        )
        cls._validate_unique_instance(component, expanded_instance_spec, rloc)
        return cls(component, expanded_instance_spec, rloc)

    def to_toml_dict(self) -> dict:
        """Transform to TOML structure as a Python dict"""
        # transformation for TOML
        # {'component': [instance]} -> [[component]]
        return {self.component: [self._instance_spec]}

    def to_toml_file(self, filename: str) -> None:
        """Write spec object to toml file"""
        obj_as_dict = self.to_toml_dict()
        with open(filename, "w", encoding="utf-8") as f:
            dump(obj_as_dict, f)

    def __getitem__(self, key: str):
        """Return value from key.
        Raises KeyError if key does not exist"""
        return self._instance_spec[key]

    def __getattr__(self, attrib: str):
        """Return the spec object's specified attribute.
        Raises AttributeError if it does not exist"""
        try:
            return self._instance_spec[attrib]
        except KeyError as e:
            raise AttributeError(f"{attrib} is not an attribute of Spec") from e
