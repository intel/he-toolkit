# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import pytest
from filecmp import cmp as compare_files

from .context import spec
from spec import Spec, InvalidSpec


def test_transform_spec_to_toml_dict():
    """This method happens to be useful in other tests.
    Avoids having to write to files."""
    expected = {"hexl": [{"name": "bob"}]}
    spec = Spec.from_instance_spec("hexl", expected["hexl"][0], rloc="")
    assert spec.to_toml_dict() == expected


def test_parse_basic_spec(create_basic_spec_file):
    """The most basic test to check that a spec object is created"""
    filepath, expected_dict = create_basic_spec_file
    spec_generator = Spec.from_toml_file(filepath, rloc="", recipe_arg_dict={})
    spec = next(spec_generator)
    assert spec.to_toml_dict() == expected_dict


def test_when_name_not_given():
    """The name attribute for a component must always be provided."""
    expected = {"hexl": [{}]}
    with pytest.raises(InvalidSpec) as execinfo:
        Spec.from_instance_spec("hexl", expected["hexl"][0], rloc="")
    assert "'name' was not provided for instance" == str(execinfo.value)


def test_basic_substitutions_are_expanded():
    """The attribs need to have substitution keys expanded"""
    # Purposely put 'another' before 'something'.
    expected = {
        "hexl": [
            {
                "version": "2",
                "name": "bob%version%",
                "another": "start-%something%-end",
                "something": "bla/%name%/bla",
            }
        ]
    }
    spec = Spec.from_instance_spec("hexl", expected["hexl"][0], rloc="")
    assert spec["name"] == "bob2"
    assert spec["something"] == "bla/bob2/bla"
    assert spec["another"] == "start-bla/bob2/bla-end"


def test_write_spec_to_toml_file(create_basic_spec_file, tmp_path):
    """Compare with manually written TOML file"""
    path_to_expected_file, expected_dict = create_basic_spec_file
    spec = Spec.from_instance_spec("hexl", expected_dict["hexl"][0], rloc="")
    path_to_spec_file = (tmp_path / "spec.toml").resolve()
    spec.to_toml_file(path_to_spec_file)
    assert compare_files(path_to_spec_file, path_to_expected_file)


def test_dependency_substitutions_are_expanded(tmp_path):
    """Dependency substitutions cross component boundaries"""
    # Create a depedency
    dep = {"hexl": [{"name": "bob", "export_thing": "someinfo"}]}
    rloc = tmp_path.resolve()
    # component / instance
    dep_loc = tmp_path / "hexl/bob"
    # Creates missing directories
    dep_loc.mkdir(parents=True)
    dep_spec = Spec.from_instance_spec("hexl", dep["hexl"][0], rloc)
    # Write depedency spec to file
    dep_spec.to_toml_file((dep_loc / "hekit.spec").resolve())

    expected = {
        "somelib": [
            {
                "name": "alice",
                # component / instance
                "dep": "hexl/bob",
                # should work in tandem with basic substitution
                "something": "bla/%name%/bla --dep=$%dep%/export_thing$",
            }
        ]
    }
    spec = Spec.from_instance_spec("somelib", expected["somelib"][0], rloc)
    assert spec["something"] == f"bla/alice/bla --dep={dep_loc}/someinfo"


def test_add_component_repo_location_to_inits_and_exports():
    """Components are built in a component repo, a dedicated space
    that can be changed"""
    expected = {
        "hexl": [
            {
                "name": "bob",
                "something": "bla/%name%/bla",
                "init_something": "bla/%name%/bla",
                "export_something": "blu/%name%/blu",
            }
        ]
    }
    rloc = "/home/some_user"
    spec = Spec.from_instance_spec("hexl", expected["hexl"][0], rloc)
    assert spec["something"] == "bla/bob/bla"
    # rloc/component/instance
    assert spec["init_something"] == f"{rloc}/hexl/bob/bla/bob/bla"
    assert spec["export_something"] == f"{rloc}/hexl/bob/blu/bob/blu"


def test_basic_user_substitutions_are_expanded(mocker):
    """The attribs need to have substitution keys expanded"""
    # Purposely put 'another' before 'something'.
    exp_version = "2.3.6"
    exp_name = "Charles"
    mock_input = mocker.patch("spec.input")
    mock_input.side_effect = [exp_version, exp_name]

    expected = {
        "hexl": [
            {
                "version": "!version!",
                "name": "bob!name!",
                "another": "start-%version%-%init_something%-end",
                "init_something": "bla/%name%/bla",
            }
        ]
    }
    spec = Spec.from_instance_spec("hexl", expected["hexl"][0], rloc="")
    assert spec["name"] == f"bob{exp_name}"
    assert spec["init_something"] == f"bla/bob{exp_name}/bla"
    assert spec["another"] == f"start-{exp_version}-bla/bob{exp_name}/bla-end"


def test_user_substitutions_are_expanded_to_init(mocker):
    """Components are built in a component repo, a dedicated space
    that can be changed"""
    exp_name = "bob"
    exp_version = "1.2.5"
    mock_input = mocker.patch("spec.input")
    mock_input.return_value = exp_name

    expected = {
        "hexl": [
            {
                "name": "!name!",
                "version": "!version!",
                "something": "bla/%name%/bla",
                "init_something": "bla/%name%/bla",
                "export_something": "blu/%version%/blu",
            }
        ]
    }
    rloc = "/home/some_user"
    Spec.recipe_arg_dict = {"version": exp_version}
    spec = Spec.from_instance_spec("hexl", expected["hexl"][0], rloc)
    mock_input.assert_called_once()
    assert spec["something"] == f"bla/{exp_name}/bla"
    # rloc/component/instance
    assert spec["init_something"] == f"{rloc}/hexl/{exp_name}/bla/{exp_name}/bla"
    assert spec["export_something"] == f"{rloc}/hexl/{exp_name}/blu/{exp_version}/blu"


@pytest.fixture
def create_basic_spec_file(tmp_path):
    """Create TOML file of one instance"""
    filepath = tmp_path / "basic.toml"
    with filepath.open("w") as f:
        f.write("[[hexl]]\n")
        f.write('name = "x.y.z"\n')
        f.write("skip = true\n")
        f.write('fetch = "some-url"\n')
        f.write('build = "some-cmd"\n')
        f.write("\n")  # Parser inserts this new line

    expected_dict = {
        "hexl": [
            {"name": "x.y.z", "skip": True, "fetch": "some-url", "build": "some-cmd"}
        ]
    }

    return filepath.resolve(), expected_dict
