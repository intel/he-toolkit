# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import pytest
from filecmp import cmp as compare_files
from pathlib import Path

from .context import spec
from spec import Spec, InvalidSpecError


def test_transform_spec_to_toml_dict():
    """This method happens to be useful in other tests.
    Avoids having to write to files."""
    input_dict = {"hexl": [{"name": "bob"}]}
    expected_dict = {
        "hexl": [
            {
                "name": "bob",
                "skip": False,
                "pre_fetch": "",
                "fetch": "",
                "post_fetch": "",
                "pre_build": "",
                "build": "",
                "post_build": "",
                "pre_install": "",
                "install": "",
                "post_install": "",
                "init_fetch_dir": "fetch",
                "init_build_dir": "build",
                "init_install_dir": "build",
            }
        ]
    }
    spec = Spec.from_instance_spec("hexl", input_dict["hexl"][0], rloc="")
    assert spec.to_toml_dict() == expected_dict


def test_parse_basic_spec(create_basic_spec_file):
    """The most basic test to check that a spec object is created"""
    filepath, expected_dict = create_basic_spec_file
    spec_generator = Spec.from_toml_file(filepath, rloc="", recipe_arg_dict={})
    spec = next(spec_generator)
    assert spec.to_toml_dict() == expected_dict


def test_when_name_not_given():
    """The name attribute for a component must always be provided."""
    expected = {"hexl": [{}]}
    with pytest.raises(InvalidSpecError) as execinfo:
        Spec.from_instance_spec("hexl", expected["hexl"][0], rloc="")
    assert "'name' was not provided for instance" == str(execinfo.value)


def test_when_skip_not_boolean():
    expected = {"hexl": [{"name": "bob", "skip": "False"}]}
    with pytest.raises(InvalidSpecError) as execinfo:
        Spec.from_instance_spec("hexl", expected["hexl"][0], rloc="")
    assert "'skip' not of type bool" == str(execinfo.value)


def test_when_attribute_not_string():
    expected = {"hexl": [{"name": "bob", "build": "build", "fetch": False}]}
    with pytest.raises(InvalidSpecError) as execinfo:
        Spec.from_instance_spec("hexl", expected["hexl"][0], rloc="")
    assert "'fetch' is not a string" == str(execinfo.value)


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
    mock_input.side_effect = [exp_name, exp_version]

    expected = {
        "hexl": [
            {
                "version": "!version!",
                "name": "bob!name!",
                "another": "start-!version!-%init_something%-end",
                "init_something": "bla/%name%/bla",
            }
        ]
    }
    spec = Spec.from_instance_spec("hexl", expected["hexl"][0], rloc="")
    assert spec["name"] == f"bob{exp_name}"
    assert spec["init_something"] == f"bla/bob{exp_name}/bla"
    assert spec["another"] == f"start-{exp_version}-bla/bob{exp_name}/bla-end"
    assert 2 == mock_input.call_count


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


def test_validate_unique_instance_no_file():
    """Verify that the function continues without errors
    if hekit.spec file does not exist"""
    act_comp = "comp"
    act_inst = {"name": "test"}
    act_rloc = "/home"

    Spec._validate_unique_instance(act_comp, act_inst, act_rloc)


def test_validate_unique_instance_same_values(mocker):
    """Verify that the function continues without errors
    if the instance is the same as the previous one"""
    mock_read_spec = mocker.patch("spec.read_spec")
    mock_read_spec.return_value = {"name": "test", "option": "debug"}
    act_comp = "comp"
    act_inst = {"name": "test", "option": "debug"}
    act_rloc = "/home"

    Spec._validate_unique_instance(act_comp, act_inst, act_rloc)

    mock_read_spec.assert_called_once()


def test_validate_unique_instance_different_values(mocker):
    """Verify it triggers InvalidSpec exception when
    the instance is not the same as the previous one"""
    mock_read_spec = mocker.patch("spec.read_spec")
    mock_read_spec.return_value = {"name": "test", "option": "debug"}
    act_comp = "comp"
    act_inst = {"name": "test", "option": "release"}
    act_rloc = "/home"

    with pytest.raises(InvalidSpecError) as execinfo:
        Spec._validate_unique_instance(act_comp, act_inst, act_rloc)

    mock_read_spec.assert_called_once()
    assert (
        "comp/test is already present but it was executed with different options"
        in str(execinfo.value)
    )


def test_from_toml_file_tsort(mocker):
    """Verify dependencies are installed first"""
    tests_path = Path(__file__).resolve().parent
    mock_read_spec = mocker.patch("spec.read_spec")
    mock_read_spec.return_value = {"export_install_dir": "", "export_cmake": ""}
    mock_validate_unique = mocker.patch("spec.Spec._validate_unique_instance")
    exp_keys_list = ["ntl", "hexl", "hexl", "helib", "palisade", "gsl", "zstd", "seal"]
    filepath = f"{tests_path}/input_files/test_tsort.toml"

    specs = list(Spec.from_toml_file(filepath, rloc="", recipe_arg_dict={}))

    assert 6 == mock_read_spec.call_count
    assert 8 == mock_validate_unique.call_count
    assert len(specs) == len(exp_keys_list)
    for exp_key, spec in zip(exp_keys_list, specs):
        spec_as_dict = spec.to_toml_dict()
        assert exp_key in spec_as_dict.keys()


@pytest.fixture
def create_basic_spec_file(tmp_path):
    """Create TOML file of one instance"""
    filepath = tmp_path / "basic.toml"
    with filepath.open("w") as f:
        f.write("[[hexl]]\n")
        f.write('name = "x.y.z"\n')
        f.write("skip = true\n")
        f.write('pre_fetch = ""\n')
        f.write('fetch = "some-url"\n')
        f.write('post_fetch = ""\n')
        f.write('pre_build = ""\n')
        f.write('build = "some-cmd"\n')
        f.write('post_build = ""\n')
        f.write('pre_install = ""\n')
        f.write('install = ""\n')
        f.write('post_install = ""\n')
        f.write('init_fetch_dir = "fetch"\n')
        f.write('init_build_dir = "build"\n')
        f.write('init_install_dir = "build"\n')
        f.write("\n")  # Parser inserts this new line

    expected_dict = {
        "hexl": [
            {
                "name": "x.y.z",
                "skip": True,
                "fetch": "some-url",
                "build": "some-cmd",
                "pre_fetch": "",
                "post_fetch": "",
                "pre_build": "",
                "post_build": "",
                "pre_install": "",
                "install": "",
                "post_install": "",
                "init_fetch_dir": "fetch",
                "init_build_dir": "build",
                "init_install_dir": "build",
            }
        ]
    }

    return filepath.resolve(), expected_dict
