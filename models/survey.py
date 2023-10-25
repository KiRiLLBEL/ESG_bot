from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import relationship

from .base import Base

class Survey(Base):
    __tablename__ = 'surveys'
    survey_id = Column(Integer, primary_key=True)
    title = Column(String)
    theme_id = Column(Integer, ForeignKey('themes.theme_id'))
    score = Column(Integer)
    type = Column(Enum("business", "person", "task", name='survey_type'))
    questions = relationship('Question', back_populates='survey')
    theme = relationship('Theme', back_populates='surveys')
    users_survey = relationship('UserSurvey', back_populates='survey')

class Question(Base):
    __tablename__ = 'questions'
    question_id = Column(Integer, primary_key=True)
    text = Column(String)
    survey_id = Column(Integer, ForeignKey('surveys.survey_id'))
    survey = relationship('Survey', back_populates='questions')
    options = relationship('Option', back_populates='question')
    answers = relationship('AnswerSurvey', back_populates='question')

class Option(Base):
    __tablename__ = 'options'
    option_id = Column(Integer, primary_key=True)
    text = Column(String)
    question_id = Column(Integer, ForeignKey('questions.question_id'))
    question = relationship('Question', back_populates='options')
    answers = relationship('AnswerSurvey', back_populates='option')
