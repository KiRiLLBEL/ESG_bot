from sqlalchemy import Column, Integer, String, BigInteger, Enum, Date, ForeignKey
from sqlalchemy.orm import relationship

from .base import Base


class UserTask(Base):
    __tablename__ = "users_tasks"

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.user_id"))
    task_id = Column(Integer, ForeignKey("tasks.task_id"))
    status = Column(Enum("favorite", "active", "complete", name='task_type'))
    date = Column(Date)
    task = relationship('Task', back_populates='users_tasks')
    user = relationship('User', back_populates='users_tasks')
