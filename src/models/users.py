from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship, Mapped
from config.db import Base
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable



class User(SQLAlchemyBaseUserTable[int], Base):
    """Модель пользователя"""
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username: Mapped[str] = Column(
        String(length=320), unique=True, index=True, nullable=False
    )
    orders = relationship("Order", back_populates='owner')
