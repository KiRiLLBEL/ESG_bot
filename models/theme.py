from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from .base import Base

class Theme(Base):
    __tablename__ = "themes"
    theme_id = Column(Integer, primary_key=True)
    title = Column(String)
    tasks = relationship('Task', back_populates='theme')
    surveys = relationship('Survey', back_populates='theme')