from sqlalchemy import Column, Integer, ForeignKey, BigInteger, Enum, Date, String
from sqlalchemy.orm import relationship

from .base import Base

class EventTheme(Base):
    __tablename__ = "events_themes"
    event_theme_id = Column(Integer, primary_key=True)
    title = Column(String)
    events = relationship("Event", back_populates='theme')


class Event(Base):
    __tablename__ = "events"
    event_id = Column(Integer, primary_key=True)
    title = Column(String)
    description = Column(String)
    place = Column(String)
    capacity = Column(Integer)
    date = Column(Date)
    organizer = Column(String)
    value = Column(Integer)
    image_url = Column(String)
    theme_id = Column(Integer, ForeignKey("events_themes.event_theme_id"))
    theme = relationship("EventTheme", back_populates='events')
    users_events = relationship("UserEvent", back_populates='event')

class UserEvent(Base):
    __tablename__ = "users_events"
    users_events_id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey("events.event_id"))
    user_id = Column(BigInteger, ForeignKey("users.user_id"))
    status = Column(Enum("favorite", "active", "complete", name='event_type'))
    user = relationship("User", back_populates='events')
    event = relationship("Event", back_populates='users_events')