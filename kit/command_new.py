# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

"""This module creates the directory structure and initial files to set up a new project"""

from shutil import copytree
from pathlib import Path
from re import findall
from spec import Spec
from constants import Constants


def create_toml_template(
    project_name: str, project_path: Path, toml_path: Path
) -> None:
    """Create a template of a toml file"""
    toml_path.parent.mkdir(parents=True, exist_ok=False)

    component = "projects"
    instance_spec = {
        "name": f"{project_name}",
        "src_dir": f"{project_path}",
        "pre-build": "cmake -S %src_dir% -B %init_build_dir% -DFLAG=TBD",
        "build": "cmake --build %init_build_dir% -j",
    }

    # Write toml file
    specs = Spec(component, instance_spec, "")
    specs.to_toml_file(toml_path)


def create_cmake_template(project_name: str, cmake_path: Path) -> None:
    """Create a template of a cmake file"""
    lines = (
        f"project({project_name} LANGUAGES CXX)\n\n"
        f"cmake_minimum_required(VERSION {Constants.cmake_min_version} FATAL_ERROR)\n\n"
        f"set(CMAKE_CXX_STANDARD {Constants.cmake_cxx_standard})\n"
        "set(CMAKE_CXX_EXTENSIONS OFF)\n"
        "set(CMAKE_CXX_STANDARD_REQUIRED ON)\n\n"
        "#find_package(helib REQUIRED)\n"
        "#find_package(SEAL REQUIRED)\n\n"
        "file(GLOB SRCS ${CMAKE_CURRENT_SOURCE_DIR}/src/*.cpp)\n"
        f"add_executable({project_name} ${{SRCS}})\n\n"
        f"target_include_directories({project_name} PRIVATE ${{CMAKE_CURRENT_SOURCE_DIR}}/include)\n\n"
        f"#target_link_libraries({project_name} PRIVATE helib)\n"
        f"#target_link_libraries({project_name} PRIVATE SEAL::seal)\n"
    )

    # Write the cmake file
    with cmake_path.open("w") as cmake_file:
        for line in lines:
            cmake_file.write(line)


def modify_cmake_file(project_name: str, cmake_path: Path) -> None:
    """Modify a cmake file with the project name"""
    text = cmake_path.read_text()
    executable_name = findall(r"add_executable\((.*) .*\)", text)
    if executable_name:
        text = text.replace(executable_name[0], project_name)
        cmake_path.write_text(text)


def create_directory_structure(project_name: str, project_path: Path) -> None:
    """Create directory structure and initial files"""
    structure = {
        project_path: "README.md",
        project_path / "src": f"{project_name}.cpp",
        project_path / "include": f"{project_name}.h",
    }

    for path, file in structure.items():
        path.mkdir(parents=True, exist_ok=False)
        file_path = path / file
        file_path.touch(mode=438, exist_ok=False)


def create_new_project(args) -> None:
    """create a new project"""
    project_name = args.name
    project_path = Path(args.directory).resolve().expanduser()
    project_path = project_path / "projects" / f"{project_name}"
    toml_path = project_path / "recipes" / f"{project_name}.toml"
    cmake_path = project_path / "CMakeLists.txt"

    try:
        if args.based_on:
            example_path = (
                args.hekit_root_dir / "he-samples" / "examples" / args.based_on
            )
            copytree(example_path, project_path, dirs_exist_ok=False)
            modify_cmake_file(project_name, cmake_path)
        else:
            # Create a new project
            create_directory_structure(project_name, project_path)
            create_cmake_template(project_name, cmake_path)

        create_toml_template(project_name, project_path, toml_path)

    except FileExistsError:
        print(f"Project {project_path} already exists")


def set_new_subparser(subparsers, hekit_root_dir):
    """create the parser for the 'new' command"""
    parser_new = subparsers.add_parser("new", description="create a new project")
    parser_new.add_argument("name", type=str, help="project name")
    parser_new.add_argument(
        "--directory", type=str, default=".", help="location of the new project"
    )
    parser_new.add_argument(
        "--based-on",
        type=str,
        help="base project",
        choices=["logistic-regression", "psi", "secure-query"],
    )
    parser_new.set_defaults(fn=create_new_project, hekit_root_dir=hekit_root_dir)
