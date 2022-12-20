"""Define a Config class for the environment settings"""

# https://flask.palletsprojects.com/en/2.2.x/config/
from os import environ, path

basedir = path.abspath(path.dirname(__file__))


class Config:
    """Defne environment settings"""

    FLASK_DEBUG = environ["FLASK_DEBUG"]
    SQLALCHEMY_DATABASE_URI = environ["SQLALCHEMY_DATABASE_URI"]
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = environ["SECRET_KEY"]
    JWT_SECRET_KEY = "super-secret"  # nosec B105

    KAFKA_CLUSTER_HOST = environ["KAFKA_CLUSTER_HOST"]
    KAFKA_CLUSTER_INBOUND_TOPIC = environ["KAFKA_CLUSTER_INBOUND_TOPIC"]
    KAFKA_CLUSTER_MAX_BYTES = environ["KAFKA_CLUSTER_MAX_BYTES"]

    HEKIT_CREATE_CONTEXT_PATH = environ["HEKIT_CREATE_CONTEXT_PATH"]
    HEKIT_ENCODE_PATH = environ["HEKIT_ENCODE_PATH"]
    HEKIT_ENCRYPT_PATH = environ["HEKIT_ENCRYPT_PATH"]

    KEYS_PATH = environ["KEYS_PATH"]
    STORAGE_PATH = environ["STORAGE_PATH"]
