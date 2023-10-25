from sqlalchemy import Column, Integer, String, Identity, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class Task(Base):
    __tablename__ = "tasks"
    task_id = Column(Integer, Identity(start=1), primary_key=True, autoincrement=True)
    theme_id = Column(Integer, ForeignKey("themes.theme_id"))
    title = Column(String)
    description = Column(String)
    value = Column(Integer)
    theme = relationship('Theme', back_populates='tasks')
    users_tasks = relationship('UserTask', back_populates='task')
