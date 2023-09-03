from sqlalchemy import Column, Integer, BigInteger, String, Boolean

from .base import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(BigInteger, primary_key=True, unique=True, autoincrement=False)
    name = Column(String)
    status = Column(String)
    score = Column(Integer, default=0)
    quiz = Column(Boolean)
