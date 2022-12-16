"""Define config class for kafka and Database settings"""

# https://flask.palletsprojects.com/en/2.2.x/config/
from os import environ, path

basedir = path.abspath(path.dirname(__file__))


class Config:
    """Define kafka and Database configuration"""

    SQLALCHEMY_DATABASE_URI_NO_PROTOCOL = environ["SQLALCHEMY_DATABASE_URI_NO_PROTOCOL"]
    SQLALCHEMY_DATABASE_URI = environ["SQLALCHEMY_DATABASE_URI"]
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    KAFKA_CLUSTER_HOST = environ["KAFKA_CLUSTER_HOST"]
    KAFKA_CLUSTER_INBOUND_TOPIC = environ["KAFKA_CLUSTER_INBOUND_TOPIC"]
    KAFKA_CLUSTER_MAX_BYTES = environ["KAFKA_CLUSTER_MAX_BYTES"]
