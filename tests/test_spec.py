# Copyright (C) 2020-2021 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import pytest
from kit.spec import Spec, InvalidSpec


def test_transform_spec_to_toml_dict():
    """This method happens to be useful in other tests.
    Avoids having to write to files."""
    expected = {"hexl": {"name": "bob"}}
    spec = Spec.from_instance_spec("hexl", expected["hexl"])
    assert spec.to_toml_dict() == expected


def test_parse_basic_spec(create_basic_spec_file):
    """The most basic test to check that a spec object is created"""
    filepath, expected_dict = create_basic_spec_file
    spec_generator = Spec.from_toml_file(filepath)
    spec = next(spec_generator)
    assert spec.to_toml_dict() == expected_dict


def test_when_name_not_given():
    """The name attribute for a component must always be provided."""
    expected = {"hexl": {}}
    with pytest.raises(InvalidSpec) as execinfo:
        Spec.from_instance_spec("hexl", expected["hexl"])
    assert "'name' was not provided for instance" == str(execinfo.value)


def test_basic_substitutions_are_expanded():
    """The init_ and export_ attribs need to have expanded paths"""
    # Purposely put 'another' before 'something'.
    expected = {
        "hexl": {
            "name": "bob",
            "another": "start-%something%-end",
            "something": "/bla/%name%/bla",
        }
    }
    spec = Spec.from_instance_spec("hexl", expected["hexl"])
    assert spec["something"] == "/bla/bob/bla"
    assert spec["another"] == "start-/bla/bob/bla-end"


# def test_dependency_substitutions_are_expanded():
# assert False


@pytest.fixture
def create_basic_spec_file(tmp_path):
    """Create tmp TOML file"""
    filepath = tmp_path / "basic.toml"
    with filepath.open("w") as f:
        f.write("[[hexl]]\n")
        f.write('name = "x.y.z"\n')
        f.write("skip = true\n")
        f.write('fetch = "some-url"\n')
        f.write('build = "some-cmd"\n')

    expected_dict = {
        "hexl": {
            "name": "x.y.z",
            "skip": True,
            "fetch": "some-url",
            "build": "some-cmd",
        }
    }

    return filepath.resolve(), expected_dict
