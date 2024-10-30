from pydantic import BaseModel, Field
from typing import Optional
from models.orders import OrderStatus


class OrderCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=255)
    status: OrderStatus = Field(default=OrderStatus.pending)
    user_id: int


class OrderList(OrderCreate):
    id: int


class OrderUpdateStatus(BaseModel):
    status: OrderStatus