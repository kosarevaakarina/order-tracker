import enum
from datetime import datetime

from sqlalchemy import Column, Integer, String, Enum, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship
from config.db import Base


class OrderStatus(str, enum.Enum):
    """Статус заказа"""
    pending = 'pending'
    in_progress = 'in_progress'
    done = 'done'


class Order(Base):
    """Модель Заказа"""
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    status = Column(Enum(OrderStatus), default=OrderStatus.pending)
    user_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates='orders')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    price = Column(Float)
