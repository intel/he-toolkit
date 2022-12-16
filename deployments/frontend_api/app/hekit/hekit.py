"""Hekit"""
import subprocess
import time
from os import environ


def encode(user_id: str, job_id: str) -> str:
    """Encode"""
    config_toml = f"{environ['KEYS_PATH']}config.toml"
    query = f"{environ['STORAGE_PATH']}{user_id}/{job_id}/{job_id}_query.csv"
    query_ptxt = f"{environ['STORAGE_PATH']}{user_id}/{job_id}/{job_id}_query.ptxt"

    start_time = time.time()
    with open(
        query_ptxt,
        "w",
        encoding="utf-8",
    ) as file_descriptor:
        subprocess.run(
            [environ["HEKIT_ENCODE_PATH"], "--config", config_toml, query],
            stdout=file_descriptor,
            check=True,
        )

    return time.time() - start_time


def encrypt(user_id: str, job_id: str) -> str:
    """Encrypt"""
    public_key = f"{environ['KEYS_PATH']}key.pk"
    query_ptxt = f"{environ['STORAGE_PATH']}{user_id}/{job_id}/{job_id}_query.ptxt"
    query_ctxt = f"{environ['STORAGE_PATH']}{user_id}/{job_id}/{job_id}_query.ctxt"

    start_time = time.time()
    subprocess.run(
        [environ["HEKIT_ENCRYPT_PATH"], public_key, query_ptxt, "-o", query_ctxt],
        check=True,
    )

    return time.time() - start_time


def decode(user_id: str, job_id: str):
    """Decode"""
    config_toml = f"{environ['KEYS_PATH']}config.toml"
    result_file = (
        f"{environ['STORAGE_PATH']}{user_id}/{job_id}/{job_id}_result_file.ptxt"
    )
    final = f"{environ['STORAGE_PATH']}{user_id}/{job_id}/{job_id}_final"

    start_time = time.time()
    with open(final, "wb") as file_descriptor:
        subprocess.run(
            [environ["HEKIT_DECODE_PATH"], "--config", config_toml, result_file],
            stdout=file_descriptor,
            check=True,
        )

    return time.time() - start_time


def decrypt(user_id: str, job_id: str) -> str:
    """Decrypt"""
    secret_key = f"{environ['KEYS_PATH']}key.sk"
    result_file = (
        f"{environ['STORAGE_PATH']}{user_id}/{job_id}/{job_id}_result_file.ptxt"
    )
    output = f"{environ['STORAGE_PATH']}{user_id}/{job_id}/{job_id}_output"
    start_time = time.time()
    subprocess.run(
        [environ["HEKIT_DECRYPT_PATH"], "-o", result_file, secret_key, output],
        check=True,
    )

    return time.time() - start_time
