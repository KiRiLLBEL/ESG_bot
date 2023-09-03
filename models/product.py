from sqlalchemy import Column, Integer, Boolean, BigInteger, String

from .base import Base


class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    price = Column(Integer)
    image_url = Column(String)
