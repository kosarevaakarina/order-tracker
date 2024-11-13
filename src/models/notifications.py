import enum
from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Enum, String
from sqlalchemy.orm import relationship
from config.db import Base


class NotificationType(str, enum.Enum):
    """Статус заказа"""
    create = 'create'
    update = 'update'


class Notification(Base):
    """Модель Рассылки"""
    __tablename__ = 'notifications'
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    type = Column(Enum(NotificationType))
    message = Column(String)

    orders = relationship("Order", back_populates='notifications')