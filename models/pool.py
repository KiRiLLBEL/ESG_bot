from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from .base import Base

class Survey(Base):
    __tablename__ = 'surveys'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    theme = Column(String)
    score = Column(Integer)
    questions = relationship('Question', back_populates='survey', lazy='joined')

class Question(Base):
    __tablename__ = 'questions'
    id = Column(Integer, primary_key=True)
    text = Column(String)
    survey_id = Column(Integer, ForeignKey('surveys.id'))
    survey = relationship('Survey', back_populates='questions')
    options = relationship('Option', back_populates='question', lazy='joined')

class Option(Base):
    __tablename__ = 'options'
    id = Column(Integer, primary_key=True)
    text = Column(String)
    question_id = Column(Integer, ForeignKey('questions.id'))
    question = relationship('Question', back_populates='options')
