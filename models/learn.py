from sqlalchemy import Column, Integer, ForeignKey, BigInteger, Enum, Date, String
from sqlalchemy.orm import relationship

from .base import Base

class LearnTheme(Base):
    __tablename__ = "learn_themes"
    learn_theme_id = Column(Integer, primary_key=True)
    title = Column(String)
    courses = relationship("LearnCourse", back_populates='learn_theme')
    materials = relationship("LearnMaterial", back_populates='learn_theme')


class LearnCourse(Base):
    __tablename__ = "learn_courses"
    learn_courses_id = Column(Integer, primary_key=True)
    title = Column(String)
    url = Column(String)
    learn_theme_id = Column(Integer, ForeignKey("learn_themes.learn_theme_id"))
    learn_theme = relationship("LearnTheme", back_populates="courses")

class LearnMaterial(Base):
    __tablename__ = "learn_materials"
    learn_materials_id = Column(Integer, primary_key=True)
    description = Column(String)
    url = Column(String)
    learn_theme_id = Column(Integer, ForeignKey("learn_themes.learn_theme_id"))
    learn_theme = relationship("LearnTheme", back_populates="materials")