from sqlalchemy import Column, Integer, String, BigInteger

from .base import Base


class TaskStatus(Base):
    __tablename__ = "tasks_status"

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger)
    uid = Column(Integer)
    name = Column(String)
    status = Column(String)
