from sqlalchemy import Column, Integer, String, Identity

from .base import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, Identity(start=100000), primary_key=True,)
    uid = Column(Integer)
    name = Column(String)
    description = Column(String)
    theme = Column(String)
    value = Column(Integer)

