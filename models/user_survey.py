from sqlalchemy import Column, Integer, ForeignKey, BigInteger, Enum, Date
from sqlalchemy.orm import relationship

from .base import Base

class UserSurvey(Base):
    __tablename__ = 'users_surveys'
    users_surveys_id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, ForeignKey('users.user_id'))
    survey_id = Column(Integer, ForeignKey('surveys.survey_id'))
    status = Column(Enum('favorite', 'active', 'complete', name='survey_status_type'))
    date = Column(Date)
    survey = relationship('Survey', back_populates='users_survey')
    user = relationship('User', back_populates='user_surveys')
    answers = relationship('AnswerSurvey', back_populates='user_survey')
class AnswerSurvey(Base):
    __tablename__ = 'answers_surveys'
    answers_surveys_id = Column(Integer, primary_key=True)
    users_surveys_id = Column(Integer, ForeignKey('users_surveys.users_surveys_id'))
    option_id = Column(Integer, ForeignKey('options.option_id'))
    question_id = Column(Integer, ForeignKey('questions.question_id'))
    user_survey = relationship('UserSurvey', back_populates='answers')
    question = relationship('Question', back_populates='answers')
    option = relationship('Option', back_populates='answers')
