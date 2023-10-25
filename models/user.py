from sqlalchemy import Column, Integer, BigInteger, String, SmallInteger, Date, Enum
from sqlalchemy.orm import relationship

from .base import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(BigInteger, primary_key=True, unique=True, autoincrement=False)
    username = Column(String)
    status = Column(Enum("business", "person", name='user_type'))
    score = Column(Integer, default=0)
    level = Column(SmallInteger, default=0)
    reg_data = Column(Date)
    users_tasks = relationship('UserTask', back_populates='user')
    user_surveys = relationship('UserSurvey', back_populates='user')
    events = relationship('UserEvent', back_populates='user')
    purchases = relationship('ShoppingSession', back_populates='user')
