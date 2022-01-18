# Copyright (C) 2020-2021 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import toml
import re
from dataclasses import dataclass


def read_spec(component, name, attrib, repo_location):
    """Return hekit.spec file as a dict"""
    path = f"{repo_location}/{component}/{name}/hekit.spec"
    spec = toml.load(path)
    return spec[attrib]


def fill_self_ref_string_dict(d, repo_path):
    """Returns a dict with str values.
    NB. Only works for flat str value dict."""

    def fill_str(s):
        """s can be a string or a list of strings"""
        if isinstance(s, str):
            symbols = re.findall(r"(%(.*?)%)", s)
            if not symbols:
                return s

            new_s = s
            for symbol, k in symbols:
                new_s = new_s.replace(symbol, fill_str(d[k]))

            return new_s
        elif isinstance(s, list):
            return [fill_str(e) for e in s]
        else:
            # Not str or list
            return s

    def fill_dep_str(s):
        """s can be a string or a list of strings"""
        if isinstance(s, str):
            symbols = re.findall(r"(\$(.*?)/(.*?)/(.*?)\$)", s)
            if not symbols:
                return s

            new_s = s
            for symbol, comp, name, k in symbols:
                # Assume finalised spec is already expanded
                sub = read_spec(comp, name, k, repo_path)
                new_s = new_s.replace(symbol, sub)

            return new_s
        elif isinstance(s, list):
            return [fill_dep_str(e) for e in s]
        else:
            # Not str or list
            return s

    return {k: fill_dep_str(fill_str(v)) for k, v in d.items()}


def fill_rloc_paths(d, repo_location):
    """Create absolute path for the top-level attribs that begin
       with 'init_' by prepending repo location"""
    for k, v in d.items():
        if k.startswith("init_") or k.startswith("export_"):
            d[k] = f"{repo_location}/{v}"
    return d


class InvalidSpec(Exception):
    """InvalidSpec exception raised for an invalid spec"""


@dataclass(frozen=True)
class Spec:
    """hekit component specification"""

    component: str
    _instance_spec: dict
    repo_location: str

    # These will be turned into property methods
    _fixed_attribs = {
        "name",
        "skip",
        # Stages
        "pre_fetch",
        "fetch",
        "post_fetch",
        "pre_build",
        "build",
        "post_build",
        "pre_install",
        "install",
        "post_install",
    }

    # Factory from TOML file
    @classmethod
    def from_toml_file(cls, filename: str, rloc: str):
        """Generator. Process spec file. Expand paths.
        Populate the fixed attribs
        and place others in dictionary."""

        toml_specs = toml.load(filename)
        for component, instance_specs in toml_specs.items():
            for instance_spec in instance_specs:
                yield cls.from_instance_spec(component, instance_spec, rloc)

    @staticmethod
    def _expand_instance(instance: dict, rloc: str):
        """Expansion operations"""
        instance = fill_self_ref_string_dict(instance, "/")
        instance = fill_rloc_paths(instance, rloc)
        return instance

    @classmethod
    def _validate_instance(cls, instance: dict):
        """Validates the instance.
        This method is gnostic about the spec"""

        # Name attrib must be provided
        if "name" not in instance.keys():
            raise InvalidSpec("'name' was not provided for instance")

        if not isinstance(instance.get("skip", False), bool):
            raise InvalidSpec("'skip' not of type bool")

        do_not_include = {"skip"}
        for attrib in cls._fixed_attribs - do_not_include:
            for_test = instance.get(attrib, str())
            if not isinstance(for_test, str):
                raise InvalidSpec(f"'{attrib}' is not a string")

    # Factory given parsed TOML python dict
    @classmethod
    def from_instance_spec(cls, component: str, instance_spec: dict, rloc: str):
        """Expand paths.
        Populate the fixed attribs and place others in dictionary."""
        cls._validate_instance(instance_spec)
        expanded_instance_spec = cls._expand_instance(instance_spec, rloc)
        return cls(component, expanded_instance_spec, rloc)

    def to_toml_file(self, filename: str):
        """Write spec object to toml file"""
        obj_as_dict = self.to_toml_dict()
        with open(filename, "w") as f:
            toml.dump(obj_as_dict, f)

    def to_toml_dict(self):
        """Transform to TOML structure as a Python dict"""
        return {self.component: self._instance_spec}

    def __getitem__(self, key: str):
        """Return value from key. Raises KeyError if key does not exist"""
        return self._instance_spec[key]


# Require func to create a non-local
def _fn(k):
    return lambda self: self._instance_spec[k]


# Attach fixed attrib properties
for method in Spec._fixed_attribs:
    setattr(Spec, method, property(_fn(method)))
