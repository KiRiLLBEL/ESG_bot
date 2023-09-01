from sqlalchemy import Column, Integer, String

from .base import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)
    uid = Column(Integer)
    name = Column(String)
    description = Column(String)
    theme = Column(String)
    value = Column(Integer)
