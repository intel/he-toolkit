"""API Module."""
from os import makedirs, environ
from subprocess import run  # nosec B404
from pathlib import Path

from flask import Flask
from flask_cors import CORS
from app.api_spec import spec
from app.models.db import db
from app.models.jwt import jwt
from app.routes.auth import auth
from app.routes.jobs import jobs
from app.swagger import SWAGGER_URL, swagger_ui_blueprint


def create_app():
    """Create app."""
    app = Flask(__name__, instance_relative_config=True)

    # Load configuration
    app.config.from_object("config.Config")

    # Ensure the instance folder exists
    try:
        makedirs(app.instance_path)
    except OSError:
        pass

    # Initialize database
    db.init_app(app)

    # Initialize JWT
    jwt.init_app(app)

    app.register_blueprint(auth, url_prefix="/auth")
    app.register_blueprint(jobs, url_prefix="/api/v1.0/jobs")

    CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
    # Register Swagger blueprint
    # https://github.com/sveint/flask-swagger-ui
    app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)

    # https://pypi.org/project/apispec-webframeworks/
    # Load blueprints to swagger

    with app.test_request_context():
        functions = (
            function
            for function_name, function in app.view_functions.items()
            if function_name != "static"
        )

        for function in functions:
            spec.path(view=function)

    # Initialize context
    # validate_context()

    return app


def validate_context():
    """Validate and creates the context"""
    if Path.exists("./test_data/test.params") is False:
        raise Exception("params file is missing!")

    if Path.exists("./test_data/test_config.toml") is False:
        raise Exception("config.toml file is missing!")

    if (Path.exists("./test.pk") is False) or (Path.exists("./test.sk") is False):
        print("Creating context")
        run(  # nosec B603
            [
                environ["HEKIT_CREATE_CONTEXT_PATH"],
                "./test_data/test.params",
                "-o",
                "test",
                "--frob-skm",
                "--info-file",
            ],
            check=True,
        )

    if Path.exists("./test_data/test_db.ptxt") is False:
        print("Encoding database")
        with open(
            "./test_data/test_db.ptxt",
            "w",
            encoding="utf-8",
        ) as f:
            run(  # nosec B603
                [
                    environ["HEKIT_ENCODE_PATH"],
                    "--server",
                    "--config",
                    "./test_data/test_config.toml",
                    "./test_data/test_db",
                ],
                check=True,
                stdout=f,
            )

    if Path.exists("./test_data/test_db.ctxt") is False:
        print("Encrypting database")
        run(  # nosec B603
            [
                environ["HEKIT_ENCRYPT_PATH"],
                "test.pk",
                "./test_data/test_db.ptxt",
                "-o",
                "./test_data/test_db.ctxt",
            ],
            check=True,
        )
