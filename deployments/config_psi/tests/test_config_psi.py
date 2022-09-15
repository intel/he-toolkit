# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import pytest
import os
from pathlib import Path
from subprocess import run
from shlex import split


def execute_process(cmd: str) -> str:
    return run(split(cmd), encoding="utf-8", capture_output=True)


def test_setup(setup):
    """Setup context, keys, and encode/encrypt server_list"""
    params_file, config_file, table_file, server_list, client_list = setup

    assert params_file.read_text() == "p=37\nm=24\nr=1\nc=2\nQbits=500\n"
    assert client_list.exists()
    assert server_list.exists()

    # Generated output
    assert server_list.with_suffix(".ctxt").exists()
    assert server_list.with_suffix(".encoded").exists()
    # Check context/keys
    pk_file = params_file.with_suffix(".pk")
    sk_file = params_file.with_suffix(".sk")
    info_file = params_file.with_suffix(".info")
    assert pk_file.exists()
    assert sk_file.exists()
    assert info_file.exists()


@pytest.mark.skip()
def test_ptxt_to_ptxt():
    cmd = f"ls"
    act_result = execute_process(cmd)
    assert not act_result.stderr
    assert 0 == act_result.returncode
    assert False


@pytest.mark.skip()
def test_ctxt_to_ptxt():
    cmd = f"ls"
    act_result = execute_process(cmd)
    assert not act_result.stderr
    assert 0 == act_result.returncode
    assert False


@pytest.mark.skip()
def test_ptxt_to_ctxt():
    cmd = f"ls"
    act_result = execute_process(cmd)
    assert not act_result.stderr
    assert 0 == act_result.returncode
    assert False


@pytest.mark.skip()
def test_ctxt_to_ctxt():
    cmd = f"ls"
    act_result = execute_process(cmd)
    assert not act_result.stderr
    assert 0 == act_result.returncode
    assert False


@pytest.fixture
def out_str() -> str:
    """Requires a 4-tuple (pipeline-combo, db-name, query-name, match-num)
       e.g. ('ctxt-to-ctxt', 'db.ctxt', 'query.ctxt', 2)"""

    return (
        "Encoding client list\n"
        "Encrypting client list\n"
        "Computing PSI\n"
        "Threads available: 1\n"
        "Loading HE Context and Public Key...Done.\n"
        "Executing %s comparison\n"
        "Reading database from file %s ...Done.\n"
        "Reading query data form file %s ...Done.\n"
        "Configuring query...Cone.\n"
        "Writing result to file resultFile ...Done.\n"
        "Decrypting result\n"
        "Decoding result\n"
        "Match on line '%d'\n"
    )


@pytest.fixture
def setup(cwd, tmp_path, test_params_and_input_data):
    """Set up context, keys, encode/encrypt input data"""

    # NOTE: Hard coded path to HElib utils installed by HE-Toolkit
    helib_utils_path = Path("~/.hekit/components/helib/psi-io/fetch/HElib/utils").expanduser()

    params = "test.params"
    config = "test_config.toml"
    table = "test.table"
    db = "test_db"
    query = "test_query"

    # Create test data and params
    params, config, table, db, query = test_params_and_input_data(params, config, table, db, query)

    # Create context
    run(
            [
                helib_utils_path / "build/bin/create-context",
                params,
                "-o",
                "test",
                "--frob-skm",
                "--info-file",
            ],
            check=True,
        )

    # Encode query
    with open(tmp_path / "test_query.ptxt", "w") as fp:
        run(
                [
                    os.environ["CONFIG_PSI_DIR"] + "/scripts/encode.py",
                    "--config",
                    config,
                    query,
                ],
                check=True,
                stdout=fp,
            )

    # Encode db
    with open(tmp_path / "test_db.ptxt", "w") as fp:
        run(
                [
                    os.environ["CONFIG_PSI_DIR"] + "/scripts/encode.py",
                    "--server",
                    "--config",
                    config,
                    db,
                ],
                check=True,
                stdout=fp,
            )

    # Encrypt query
    run(
            [
                helib_utils_path / "build/bin/encrypt",
                "test.pk",
                tmp_path / "test_query.ptxt",
                "-o",
                tmp_path / "test_query.ctxt",
            ],
            check=True,
        )

    # Encrypt db
    run(
            [
                helib_utils_path / "build/bin/encrypt",
                "test.pk",
                tmp_path / "test_db.ptxt",
                "-o",
                tmp_path / "test_db.ctxt",
            ],
            check=True,
        )

    return params.resolve(), config.resolve(), table.resolve(), db.resolve(), query.resolve()


@pytest.fixture
def test_params_and_input_data(tmp_path):
    """Create a tmp dir containing test params and input data."""

    def _create_func(params_file: str, config_file: str, table_file: str, db_file: str, query_file: str):
        # Create the test params
        params_path = tmp_path / f"{params_file}"
        params_path.write_text("p=37\nm=24\nr=1\nc=2\nQbits=500\n")

        # Create config file
        config_path = tmp_path / f"{config_file}"
        config_path.write_text("[params]\np=37\nm=24\n\n[config]\ncolumns=3\nsegments=1\n\n[columns.encoding]\ncol1='alphanumeric'\ncol2='alphabetical'\ncol3='numeric'\n\n[columns.composite]\ncol1=2\n")

        # Create table file
        table_path = tmp_path / f"{table_file}"
        table_path.write_text("TABLE(col1(2), col2, col3)\ncol1 AND (col2 OR col3)\n")

        # Create database file
        db_path = tmp_path / f"{db_file}"
        db_path.write_text("col1 col2 col3\nW5X6 YZ 78\nA1B2 CD 12\n")

        # Create query file
        query_path = tmp_path / f"{query_file}"
        query_path.write_text("col1 col2 col3\nA1B2 CD 12\nE3F4 GH 34\n")

        return params_path.resolve(), config_path.resolve(), table_path.resolve(), db_path.resolve(), query_path.resolve()

    return _create_func


@pytest.fixture
def cwd(tmp_path, request):
    os.chdir(tmp_path)
    yield
    os.chdir(request.config.invocation_dir)
