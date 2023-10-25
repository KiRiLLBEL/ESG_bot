from sqlalchemy import Column, Integer, Date, String, ForeignKey, BigInteger
from sqlalchemy.orm import relationship

from .base import Base


class Product(Base):
    __tablename__ = 'products'
    product_id = Column(Integer, primary_key=True)
    title = Column(String)
    price = Column(Integer)
    image_url = Column(String)
    carts = relationship('CartItem', back_populates='product')

class CartItem(Base):
    __tablename__ = 'cart_items'
    kart_id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.product_id"))
    purchase_id = Column(Integer, ForeignKey("shopping_session.purchase_id"))
    product = relationship('Product', back_populates='carts')
    session = relationship('ShoppingSession', back_populates='carts')

class Order(Base):
    __tablename__ = 'orders'
    order_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    session_id = Column(Integer, ForeignKey("shopping_session.purchase_id"))
    session = relationship('ShoppingSession', back_populates='order')
    start_date = Column(Date)
    end_date = Column(Date)

class ShoppingSession(Base):
    __tablename__ = "shopping_session"
    purchase_id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.user_id"))
    order = relationship('Order', back_populates='session')
    carts = relationship('CartItem', back_populates='session')
    user = relationship('User', back_populates='purchases')
    total = Column(Integer)
    create_date = Column(Date)
