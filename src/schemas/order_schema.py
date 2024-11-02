from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from models.orders import OrderStatus


class OrderCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=255)
    status: OrderStatus = Field(default=OrderStatus.pending)


class OrderInfo(OrderCreate):
    id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)


class OrderUpdateStatus(BaseModel):
    id: int
    status: OrderStatus