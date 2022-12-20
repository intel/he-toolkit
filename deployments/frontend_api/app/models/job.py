"""Job model"""
import time

from app.models.db import db


def generate_job_id() -> str:
    """Return the Job ID"""
    return str(int(time.time()))


class Job(db.Model):
    """Job Model"""

    __tablename__ = "jobs"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    org_id = db.Column(db.String(100))
    job_id = db.Column(db.String())
    status = db.Column(db.String())

    encode = db.Column(db.String())
    encrypt = db.Column(db.String())

    psi = db.Column(db.String())
    decrypt = db.Column(db.String())
    decode = db.Column(db.String())

    def serialize(self):
        """Return class attributes"""
        return {  # pylint: disable=duplicate-code
            "id": self.id,
            "user_id": self.user_id,
            "org_id": self.org_id,
            "job_id": self.job_id,
            "status": self.status,
            "encode": self.encode,
            "encrypt": self.encrypt,
            "psi": self.psi,
            "decrypt": self.decrypt,
            "decode": self.decode,
        }
