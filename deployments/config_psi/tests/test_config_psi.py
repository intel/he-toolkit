# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import pytest
import os
from pathlib import Path
from subprocess import run
from shlex import split


def decrypt_and_decode(helib_utils_path, args: list, config: Path) -> str:
    """Decrypt and decode ctxt file"""
    decrypt = [helib_utils_path / "build/bin/decrypt"]
    run(decrypt + args, check=True)
    return run(
        [
            os.environ["CONFIG_PSI_DIR"] + "/scripts/decode.py",
            "--config",
            config,
            config.parent / "resultFile.ptxt",
        ],
        encoding="utf-8",
        capture_output=True,
        check=True,
    )


def run_psi(args: list):
    """Run the PSI executable in a subprocess"""
    cmd = Path("~/.hekit/components/psi/configurable-psi/build/bin/psi").expanduser()
    return run([cmd, *args], encoding="utf-8", capture_output=True)


def test_setup(setup):
    """Test setup of context, keys, and encode/encrypt_input data"""
    params_file, config_file, table_file, server_list, client_list = setup

    assert params_file.read_text() == "p=37\nm=24\nr=1\nc=2\nQbits=500\n"
    assert config_file.exists()
    assert table_file.exists()
    assert server_list.exists()
    assert client_list.exists()

    # Generated output
    assert server_list.with_suffix(".ptxt").exists()
    assert server_list.with_suffix(".ctxt").exists()
    assert client_list.with_suffix(".ptxt").exists()
    assert client_list.with_suffix(".ctxt").exists()
    # Check context/keys
    pk_file = params_file.with_suffix(".pk")
    sk_file = params_file.with_suffix(".sk")
    info_file = params_file.with_suffix(".info")
    assert pk_file.exists()
    assert sk_file.exists()
    assert info_file.exists()


def test_ptxt_to_ptxt(setup, tmp_path, out_str):
    """Run the full ptxt-to-ptxt pipeline"""
    params_file, config_file, table_file, db, query = setup

    # Run PSI pipeline
    act_result = run_psi(
        [
            "--single-run",
            "--ptxt-query",
            "--ptxt-db",
            params_file.with_suffix(".pk"),
            table_file,
            db.with_suffix(".ptxt"),
            query.with_suffix(".ptxt"),
            tmp_path / "resultFile",
        ]
    )

    expected_result = out_str % (
        f"{db}.ptxt",
        "ptxt-to-ptxt",
        f"{query}.ptxt",
        tmp_path / "resultFile",
    )

    # Check PSI printout
    assert not act_result.stderr
    assert 0 == act_result.returncode
    assert act_result.stdout == expected_result
    # Check ptxt result
    ret = run(
        [
            os.environ["CONFIG_PSI_DIR"] + "/scripts/decode.py",
            "--config",
            config_file,
            tmp_path / "resultFile",
        ],
        encoding="utf-8",
        capture_output=True,
        check=True,
    )
    assert not ret.stderr
    assert 0 == ret.returncode
    assert ret.stdout == "Match on line '1'\nMatch on line '3'\n"


def test_ctxt_to_ptxt(setup, tmp_path, out_str, helib_utils_path):
    """Run the full ctxt-to-ptxt pipeline"""
    params_file, config_file, table_file, db, query = setup

    # Run PSI pipeline
    act_result = run_psi(
        [
            "--single-run",
            "--ptxt-db",
            params_file.with_suffix(".pk"),
            table_file,
            db.with_suffix(".ptxt"),
            query.with_suffix(".ctxt"),
            tmp_path / "resultFile",
        ]
    )

    expected_out_str = out_str % (
        f"{db}.ptxt",
        "ctxt-to-ptxt",
        f"{query}.ctxt",
        tmp_path / "resultFile",
    )

    # Check PSI printout
    assert not act_result.stderr
    assert 0 == act_result.returncode
    assert act_result.stdout == expected_out_str
    # Check ptxt result
    ret = decrypt_and_decode(
        helib_utils_path,
        [
            "-o",
            tmp_path / "resultFile.ptxt",
            params_file.with_suffix(".sk"),
            tmp_path / "resultFile",
        ],
        config_file,
    )
    assert not ret.stderr
    assert 0 == ret.returncode
    assert ret.stdout == "Match on line '1'\nMatch on line '3'\n"


def test_ptxt_to_ctxt(setup, tmp_path, out_str, helib_utils_path):
    """Run the full ptxt-to-ctxt pipeline"""
    params_file, config_file, table_file, db, query = setup

    # Run PSI pipeline
    act_result = run_psi(
        [
            "--single-run",
            "--ptxt-query",
            params_file.with_suffix(".pk"),
            table_file,
            db.with_suffix(".ctxt"),
            query.with_suffix(".ptxt"),
            tmp_path / "resultFile",
        ]
    )

    expected_result = out_str % (
        f"{str(db)}.ctxt",
        "ptxt-to-ctxt",
        f"{str(query)}.ptxt",
        tmp_path / "resultFile",
    )

    # Check PSI printout
    assert not act_result.stderr
    assert 0 == act_result.returncode
    assert act_result.stdout == expected_result
    # Check ptxt result
    ret = decrypt_and_decode(
        helib_utils_path,
        [
            "-o",
            tmp_path / "resultFile.ptxt",
            params_file.with_suffix(".sk"),
            tmp_path / "resultFile",
        ],
        config_file,
    )
    assert not ret.stderr
    assert 0 == ret.returncode
    assert ret.stdout == "Match on line '1'\nMatch on line '3'\n"


def test_ctxt_to_ctxt(setup, tmp_path, out_str, helib_utils_path):
    """Run the full ctxt-to-ctxt pipeline"""
    params_file, config_file, table_file, db, query = setup

    # Run PSI pipeline
    act_result = run_psi(
        [
            "--single-run",
            params_file.with_suffix(".pk"),
            table_file,
            db.with_suffix(".ctxt"),
            query.with_suffix(".ctxt"),
            tmp_path / "resultFile",
        ]
    )

    expected_result = out_str % (
        f"{str(db)}.ctxt",
        "ctxt-to-ctxt",
        f"{str(query)}.ctxt",
        tmp_path / "resultFile",
    )

    # Check PSI printout
    assert not act_result.stderr
    assert 0 == act_result.returncode
    assert act_result.stdout == expected_result
    # Check ptxt result
    ret = decrypt_and_decode(
        helib_utils_path,
        [
            "-o",
            tmp_path / "resultFile.ptxt",
            params_file.with_suffix(".sk"),
            tmp_path / "resultFile",
        ],
        config_file,
    )
    assert not ret.stderr
    assert 0 == ret.returncode
    assert ret.stdout == "Match on line '1'\nMatch on line '3'\n"


@pytest.fixture
def out_str() -> str:
    """Requires a 3-tuple (db-name, pipeline-combo, query-name, result-name)
    e.g. ('db.ctxt', 'ctxt-to-ctxt', 'query.ctxt', 'resultFile')"""

    return (
        "Threads available: 1\n"
        "Loading HE Context and Public Key...Done.\n"
        "Reading database from file %s ...Done.\n"
        "Configuring query...Done.\n"
        "Executing %s comparison\n"
        "Reading query data from file %s ...Done.\n"
        "Performing database lookup...Done.\n"
        "Writing result to file %s ...Done.\n"
    )


@pytest.fixture
def setup(cwd, tmp_path, helib_utils_path, test_params_and_input_data):
    """Set up context, keys, encode/encrypt input data"""

    params = "test.params"
    config = "test_config.toml"
    table = "test.table"
    db = "test_db"
    query = "test_query"

    # Create test data and params
    params, config, table, db, query = test_params_and_input_data(
        params, config, table, db, query
    )

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

    return (
        params.resolve(),
        config.resolve(),
        table.resolve(),
        db.resolve(),
        query.resolve(),
    )


@pytest.fixture
def test_params_and_input_data(tmp_path):
    """Create a tmp dir containing test params and input data."""

    def _create_func(
        params_file: str,
        config_file: str,
        table_file: str,
        db_file: str,
        query_file: str,
    ):
        # Create the test params
        params_path = tmp_path / f"{params_file}"
        params_path.write_text("p=37\nm=24\nr=1\nc=2\nQbits=500\n")

        # Create config file
        config_path = tmp_path / f"{config_file}"
        config_path.write_text(
            "[params]\np=37\nm=24\n\n[config]\ncolumns=3\nsegments=1\n\n[columns.encoding]\ncol_one='alphanumeric'\ncol_two='alphabetical'\ncol_three='numeric'\n\n[columns.composite]\ncol_one=2\n"
        )

        # Create table file
        table_path = tmp_path / f"{table_file}"
        table_path.write_text(
            "TABLE(col_one(2), col_two, col_three)\ncol_one AND (col_two OR col_three)\n"
        )

        # Create database file
        db_path = tmp_path / f"{db_file}"
        db_path.write_text("col_one col_two col_three\nW5X6 YZ 78\nA1B2 CD 12\n")

        # Create query file
        query_path = tmp_path / f"{query_file}"
        query_path.write_text(
            "col_one col_two col_three\nA1B2 CD 12\nE3F4 GH 34\nA1B2 AB 12\n"
        )

        return (
            params_path.resolve(),
            config_path.resolve(),
            table_path.resolve(),
            db_path.resolve(),
            query_path.resolve(),
        )

    return _create_func


@pytest.fixture
def helib_utils_path() -> Path:
    """Return an absolute path to a pre-built HElib utils directory"""
    # NOTE: Hard coded path to HElib utils installed by HE-Toolkit
    path = Path("~/.hekit/components/helib/psi-io/fetch/HElib/utils").expanduser()
    if path.exists():
        return path
    raise RuntimeError(
        "~/.hekit/components/helib/psi-io/fetch/HElib/utils does not exist. Please check path name and change if necessary."
    )


@pytest.fixture
def cwd(tmp_path, request):
    os.chdir(tmp_path)
    yield
    os.chdir(request.config.invocation_dir)
