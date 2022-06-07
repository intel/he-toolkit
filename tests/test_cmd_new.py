# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import pytest
from pathlib import Path
from filecmp import cmp as compare_files
from .context import new
from new import (
    create_toml_template,
    create_cmake_template,
    modify_cmake_file,
    create_directory_structure,
    create_new_project,
)


def test_create_toml_template(mocker, create_basic_spec_file, tmp_path):
    """Arrange"""
    mock_mkdir = mocker.patch.object(Path, "mkdir")
    project_name, project_path, expected_file = create_basic_spec_file
    toml_path = (tmp_path / "spec.toml").resolve()

    """Act"""
    create_toml_template(project_name, project_path, toml_path)

    """Assert"""
    mock_mkdir.assert_called_once()
    assert compare_files(expected_file, toml_path)


def test_create_cmake_template(create_basic_cmake_file, tmp_path):
    """Arrange"""
    project_name, expected_file = create_basic_cmake_file
    cmake_path = (tmp_path / "CMakeLists.txt").resolve()

    """Act"""
    create_cmake_template(project_name, cmake_path)

    """Assert"""
    assert compare_files(expected_file, cmake_path)


def test_modify_cmake_file(
    create_basic_cmake_file, create_modified_cmake_file, tmp_path
):
    """Arrange"""
    _, expected_file = create_basic_cmake_file
    modified_name, modified_file = create_modified_cmake_file

    """Act"""
    modify_cmake_file(modified_name, expected_file)

    """Assert"""
    assert compare_files(expected_file, modified_file)


def test_create_directory_structure(tmp_path):
    """Arrange"""
    project_name = "test2"
    project_path = tmp_path.resolve() / "projects" / project_name
    readme_path = project_path / "README.md"
    cpp_path = project_path / "src" / f"{project_name}.cpp"
    header_path = project_path / "include" / f"{project_name}.h"

    """Act"""
    create_directory_structure(project_name, project_path)

    """Assert"""
    assert readme_path.exists()
    assert cpp_path.exists()
    assert header_path.exists()


def test_create_new_project(tmp_path):
    """Arrange"""
    project_name = "test2"
    directory = tmp_path.resolve()
    args = MockArgs(project_name, directory, based_on="")

    project_path = directory / "projects" / project_name
    readme_path = project_path / "README.md"
    cpp_path = project_path / "src" / f"{project_name}.cpp"
    header_path = project_path / "include" / f"{project_name}.h"
    toml_path = project_path / "recipes" / f"{project_name}.toml"

    """Act"""
    create_new_project(args)

    """Assert"""
    assert readme_path.exists()
    assert cpp_path.exists()
    assert header_path.exists()
    assert toml_path.exists()


def test_create_new_project_FileExistsError(mocker, tmp_path):
    """Arrange"""
    mock_mkdir = mocker.patch.object(Path, "mkdir")
    mock_mkdir.side_effect = FileExistsError()
    mock_print = mocker.patch("new.print")

    project_name = "test2"
    directory = tmp_path.resolve()
    args = MockArgs(project_name, directory, based_on="")
    project_path = directory / "projects" / project_name

    """Act"""
    create_new_project(args)

    """Assert"""
    mock_print.assert_called_with(f"Project {project_path} already exists")


"""Utilities used by the tests"""


class MockArgs:
    def __init__(self, name, directory, based_on):
        self.name = name
        self.directory = directory
        self.based_on = based_on


@pytest.fixture
def create_basic_spec_file(tmp_path):
    """Create TOML file"""
    project_name = "test"
    project_path = "/home/project"
    filepath = (tmp_path / "basic.toml").resolve()
    with filepath.open("w") as f:
        f.write("[[projects]]\n")
        f.write(f'name = "{project_name}"\n')
        f.write(f'src_dir = "{project_path}"\n')
        f.write('pre-build = "cmake -S %src_dir% -B %init_build_dir% -DFLAG=TBD"\n')
        f.write('build = "cmake --build %init_build_dir% -j"\n')
        f.write("\n")  # Parser inserts this new line

    return project_name, project_path, filepath


def create_tmp_file(filepath, project_name):
    with filepath.open("w") as f:
        f.write(f"project({project_name} LANGUAGES CXX)\n\n")
        f.write("cmake_minimum_required(VERSION 3.13 FATAL_ERROR)\n\n")
        f.write("set(CMAKE_CXX_STANDARD 17)\n")
        f.write("set(CMAKE_CXX_EXTENSIONS OFF)\n")
        f.write("set(CMAKE_CXX_STANDARD_REQUIRED ON)\n\n")
        f.write("#find_package(helib REQUIRED)\n")
        f.write("#find_package(SEAL REQUIRED)\n\n")
        f.write("file(GLOB SRCS ${CMAKE_CURRENT_SOURCE_DIR}/src/*.cpp)\n")
        f.write(f"add_executable({project_name} ${{SRCS}})\n\n")
        f.write(
            f"target_include_directories({project_name} PRIVATE ${{CMAKE_CURRENT_SOURCE_DIR}}/include)\n\n"
        )
        f.write(f"#target_link_libraries({project_name} PRIVATE helib)\n")
        f.write(f"#target_link_libraries({project_name} PRIVATE SEAL::seal)\n")


@pytest.fixture
def create_basic_cmake_file(tmp_path):
    """Create Cmake file"""
    project_name = "test"
    filepath = (tmp_path / "basic_cmake.txt").resolve()
    create_tmp_file(filepath, project_name)

    return project_name, filepath


@pytest.fixture
def create_modified_cmake_file(tmp_path):
    """Create Cmake file"""
    project_name = "modified"
    filepath = (tmp_path / "modified_cmake.txt").resolve()
    create_tmp_file(filepath, project_name)

    return project_name, filepath
