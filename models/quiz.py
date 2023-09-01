from sqlalchemy import Column, Integer, Boolean, BigInteger, String

from .base import Base


class QuizAnswer(Base):
    __tablename__ = 'quiz'
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger)
    status = Column(String)
    question_index = Column(Integer)
    answer = Column(Boolean)
