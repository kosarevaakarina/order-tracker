import enum
from datetime import datetime

from sqlalchemy import Column, Integer, String, Enum, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship, validates
from config.db import Base


class OrderStatus(str, enum.Enum):
    pending = 'pending'
    in_progress = 'in_progress'
    done = 'done'


class Order(Base):
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

    @validates('price')
    def validate_price(self, key, value):
        if value <= 0:
            raise ValueError("Price must be greater than 0")
        return value
