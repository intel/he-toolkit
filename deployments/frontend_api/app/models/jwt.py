"""Define flask and flask_jwt  helpers"""

from flask import redirect, url_for
from flask_jwt_extended import JWTManager
from app.models.user import User

jwt = JWTManager()

# Register a callback function that takes whatever object is passed in as the
# identity when creating JWTs and converts it to a JSON serializable format.


@jwt.user_identity_loader
def user_identity_lookup(user):
    """Returns the user ID"""
    return user.id


# Register a callback function that loads a user from your database whenever
# a protected route is accessed. This should return any python object on a
# successful lookup, or None if the lookup failed for any reason (for example
# if the user has been deleted from the database).
@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    """Loads a user from your database"""    
    identity = jwt_data["sub"]
    return User.query.filter_by(id=identity).one_or_none()


@jwt.unauthorized_loader
def custom_unauthorized_response(callback):
    """Handles an unauthorized response"""
    return redirect(url_for("auth.login"))
