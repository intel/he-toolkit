"""Job model"""
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Job(Base):  # type: ignore
    """Job Model"""

    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey("public.users.id"))

    org_id = Column(String(100))
    job_id = Column(String())
    status = Column(String())

    encode = Column(String())
    encrypt = Column(String())

    psi = Column(String())
    decrypt = Column(String())
    decode = Column(String())

    def serialize(self):
        """Return the class attributes"""
        return {
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
