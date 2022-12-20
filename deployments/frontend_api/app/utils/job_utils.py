""" Job utils """
from os import environ, mkdir, path


def save_user_request(user_id: str, job_id: str, input_data: bytes) -> None:
    """Write user query to filesystem"""
    user_query = f"{environ['STORAGE_PATH']}{user_id}/{job_id}/{job_id}_query.csv"
    with open(user_query, "wb") as f:
        f.write(input_data)


def load_heql() -> str:
    """Load HEQL"""
    heql_table = f"{environ['KEYS_PATH']}query.heql"
    with open(heql_table, "r", encoding="UTF-8") as f:
        heql = f.read()

    return heql


def load_payload(user_id: str, job_id: str) -> bytes:
    """Load query cypher text on payload"""
    query_ctxt = f"{environ['STORAGE_PATH']}{user_id}/{job_id}/{job_id}_query.ctxt"
    with open(query_ctxt, "rb", encoding="UTF-8") as f:
        payload = f.read()

    return payload


def create_job_directory(user_id: str, job_id: str) -> None:
    """create job directory"""
    if not path.exists(f"{environ['STORAGE_PATH']}{user_id}/{job_id}"):
        mkdir(f"{environ['STORAGE_PATH']}{user_id}/{job_id}")


def check_user_directory(user_id: str) -> None:
    """Check if user directory exists"""
    if not path.exists(f"{environ['STORAGE_PATH']}{user_id}"):
        mkdir(f"{environ['STORAGE_PATH']}{user_id}")
