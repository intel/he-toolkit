"""Swagger"""
from flask import jsonify

from flask_swagger_ui import get_swaggerui_blueprint
from app.api_spec import spec

SWAGGER_URL = "/api/docs"
API_URL = "swagger.json"

swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL, API_URL, config={"app_name": "API"}
)


@swagger_ui_blueprint.route("/swagger.json")
def create_swagger_spec():
    """Create swagger spec"""
    return jsonify(spec.to_dict())
