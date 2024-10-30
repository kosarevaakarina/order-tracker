import enum
from sqlalchemy import Column, Integer, String, Enum, ForeignKey
from sqlalchemy.orm import relationship
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
