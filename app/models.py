from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from .db import Base
import datetime

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    email = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)
    alerts = relationship('Alert', back_populates='user')

class Alert(Base):
    __tablename__ = 'alerts'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    fuel = Column(String)
    active = Column(Boolean, default=True)
    user = relationship('User', back_populates='alerts')
    __table_args__ = (UniqueConstraint('user_id', 'fuel'),)

class Price(Base):
    __tablename__ = 'prices'
    fuel = Column(String, primary_key=True)
    price = Column(Float)
    last_changed = Column(DateTime, default=datetime.datetime.utcnow)

class PriceHistory(Base):
    __tablename__ = 'price_history'
    id = Column(Integer, primary_key=True)
    fuel = Column(String, index=True)
    price = Column(Float)
    changed_at = Column(DateTime, default=datetime.datetime.utcnow)
