# Copyright (C) 2020-2021 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import toml
from dataclasses import dataclass


class InvalidSpec(Exception):
    """InvalidSpec exception raised for an invalid spec"""


@dataclass(frozen=True)
class Spec:
    """hekit component specification"""

    component: str
    _instance_spec: dict

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
    def from_toml_file(cls, filename: str):
        """Generator. Process spec file. Expand paths.
        Populate the fixed attribs
        and place others in dictionary."""

        toml_specs = toml.load(filename)
        for component, instance_specs in toml_specs.items():
            for instance_spec in instance_specs:
                yield cls.from_instance_spec(component, instance_spec)

    @classmethod
    def _expand_instance(cls, instance):
        """Expansion operations"""
        # TODO imported funcs?
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
    def from_instance_spec(cls, component: str, instance_spec: dict):
        """Expand paths.
        Populate the fixed attribs and place others in dictionary."""
        cls._validate_instance(instance_spec)
        expanded_instance_spec = cls._expand_instance(instance_spec)
        return cls(component, expanded_instance_spec)

    def to_toml_file(self, filename: str):
        """Write spec object to toml file"""
        obj_as_dict = self.to_toml_dict()
        with open(filename, "w") as f:
            toml.dump(obj_as_dict, f)

    def to_toml_dict(self):
        """Transform to TOML structure as a Python dict"""
        return {self.component: self._instance_spec}


# Require func to create a non-local
def _fn(k):
    return lambda self: self._instance_spec[k]


# Attach fixed attrib properties
for method in Spec._fixed_attribs:
    setattr(Spec, method, property(_fn(method)))
