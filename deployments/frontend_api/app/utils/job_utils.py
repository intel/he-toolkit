""" Job utils """
from os import environ, mkdir, path


def save_user_request(user_id: str, job_id: str, input_data: bytes) -> None:
    """Write user query to filesystem"""
    user_query = f"{environ['STORAGE_PATH']}{user_id}/{job_id}/{job_id}_query.csv"
    f_user_query = open(user_query, "wb")
    f_user_query.write(input_data)
    f_user_query.close()


def load_heql() -> bytes:
    """Load HEQL"""
    heql_table = f"{environ['KEYS_PATH']}query.heql"
    f_heql_table = open(heql_table, "r")
    heql = f_heql_table.read()
    f_heql_table.close()

    return heql


def load_payload(user_id: str, job_id: str) -> bytes:
    """Load query cypher text on payload"""
    query_ctxt = f"{environ['STORAGE_PATH']}{user_id}/{job_id}/{job_id}_query.ctxt"
    f_query = open(query_ctxt, "rb")
    payload = f_query.read()
    f_query.close()

    return payload


def create_job_directory(user_id: str, job_id: str) -> None:
    """create job directory"""
    if not path.exists(f"{environ['STORAGE_PATH']}{user_id}/{job_id}"):
        mkdir(f"{environ['STORAGE_PATH']}{user_id}/{job_id}")


def check_user_directory(user_id: str) -> None:
    """Check if user directory exists"""
    if not path.exists(f"{environ['STORAGE_PATH']}{user_id}"):
        mkdir(f"{environ['STORAGE_PATH']}{user_id}")
