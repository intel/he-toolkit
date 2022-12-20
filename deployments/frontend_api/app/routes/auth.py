"""Register"""

import datetime

from flask import Blueprint, jsonify, request, Response
from flask_jwt_extended import create_access_token

from app.models.db import db
from app.models.user import User

auth = Blueprint(name="auth", import_name=__name__)


@auth.route("/login", methods=["POST"])
def login():
    """Login"""
    if request.method != "POST":
        return jsonify({"msg": "Bad request"}), 400

    email = request.json["email"]
    password = request.json["password"]
    user = User.query.filter_by(email=email).one_or_none()
    if not user or not user.check_password(password):
        return jsonify({"msg": "Bad email or password"}), 401

    additional_claims = {"username": user.username, "user_id": user.id}
    access_token = create_access_token(
        identity=user, additional_claims=additional_claims
    )
    expires_at = datetime.timedelta(minutes=15).total_seconds()

    return (
        jsonify({"access_token": access_token, "expires_at": int(expires_at)}),
        200,
    )


@auth.route("/register", methods=["POST", "GET"])
def register():
    """Register"""
    if request.method != "POST":
        return jsonify({"msg": "Bad request"}), 400

    email = request.json["email"]
    username = request.json["username"]
    password = request.json["password"]

    if User.query.filter_by(email=email).first():
        return "Email already exists"

    org_id = "0"

    user = User(email=email, username=username)
    user.set_org_id(org_id)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return Response(status=201)
