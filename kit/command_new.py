# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

"""This module XXX"""

from pathlib import Path


def create_toml_template(project_name, project_path, toml_path):
    """Create a template of a toml file"""
    lines = (
        "[[project]]\n"
        f'name = "{project_name}"\n'
        f'src_dir = "{project_path}"\n'
        'pre-build = """cmake -S %src_dir% -B %init_build_dir%\n'
        "    -DFLAG=TBD"
        'build = "cmake --build %init_build_dir% -j"\n'
    )

    with toml_path.open("a") as cmake_file:
        for line in lines:
            cmake_file.write(line)


def create_cmake_template(project_name, cmake_path):
    """Create a template of a cmake file"""
    lines = (
        f"project({project_name} LANGUAGES CXX)\n\n"
        "cmake_minimum_required(VERSION 3.13 FATAL_ERROR)\n\n"
        "set(CMAKE_CXX_STANDARD 17)\n"
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

    with cmake_path.open("a") as cmake_file:
        for line in lines:
            cmake_file.write(line)


def create_directory_structure(project_name: str, workspace: str) -> None:
    """Create XXX"""
    try:
        project_path = Path(f"{workspace}/projects/{project_name}").expanduser()
        structure = {
            project_path: ["README.ms"],
            project_path / "src": [f"{project_name}.cpp"],
            project_path / "include": [f"{project_name}.h"],
            project_path / "recipes": [],
        }

        for directory, files in structure.items():
            directory.mkdir(parents=True, exist_ok=False)
            for file in files:
                file_path = directory / file
                file_path.touch(mode=438, exist_ok=False)

        create_cmake_template(project_name, project_path / "CMakeLists.txt")
        create_toml_template(
            project_name,
            project_path,
            project_path / "recipes" / f"{project_name}.toml",
        )

    except FileExistsError:
        print(f"Project {project_path} already exists")


def create_new_project(args):
    """create a new project"""
    create_directory_structure(args.name, args.workspace)


def set_new_subparser(subparsers, hekit_root_dir):
    """create the parser for the 'remove' command"""
    parser_new = subparsers.add_parser("new", description="create a new project")
    parser_new.add_argument("name", type=str, help="proyect's name")
    parser_new.add_argument(
        "--workspace", type=str, default=hekit_root_dir, help="workspace's path"
    )
    parser_new.set_defaults(fn=create_new_project)
