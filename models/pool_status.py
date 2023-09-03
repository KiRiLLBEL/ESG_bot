from sqlalchemy import Column, Integer, String, ForeignKey, BigInteger
from sqlalchemy.orm import relationship

from .base import Base
from .pool import Survey, Question, Option


class SurveyResult(Base):
    __tablename__ = 'survey_results'
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger)
    survey_id = Column(Integer, ForeignKey('surveys.id'))
    survey = relationship('Survey', back_populates='results')
    status = Column(String)
    answers = relationship('Answer', back_populates='survey_result')

Survey.results = relationship('SurveyResult', back_populates='survey')

class Answer(Base):
    __tablename__ = 'answers'
    id = Column(Integer, primary_key=True)
    survey_result_id = Column(Integer, ForeignKey('survey_results.id'))
    survey_result = relationship('SurveyResult', back_populates='answers')
    question_id = Column(Integer, ForeignKey('questions.id'))
    question = relationship('Question', back_populates='answers')
    option_id = Column(Integer, ForeignKey('options.id'))
    option = relationship('Option', back_populates='answers')

Question.answers = relationship('Answer', back_populates='question')
Option.answers = relationship('Answer', back_populates='option')