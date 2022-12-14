"""User model"""
from app.models.db import db
from werkzeug.security import check_password_hash, generate_password_hash


class User(db.Model):
    """User Model"""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    jobs = db.relationship("Job")

    email = db.Column(db.String(80), unique=True)
    username = db.Column(db.String(100))
    org_id = db.Column(db.String(80))
    password_hash = db.Column(db.String())

    def set_org_id(self, org_id):
        """Set org id"""
        self.org_id = org_id

    def set_password(self, password):
        """Set password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check password"""
        return check_password_hash(self.password_hash, password)
