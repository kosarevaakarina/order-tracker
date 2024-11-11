from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional
from models.orders import OrderStatus


class OrderCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=255)
    status: OrderStatus = Field(default=OrderStatus.pending)
    price: float

    @field_validator('price')
    def validate_price(cls, value):
        if value <= 0:
            raise ValueError("Price must be greater than 0")
        return value


class OrderInfo(OrderCreate):
    id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)


class OrderUpdateStatus(BaseModel):
    status: OrderStatus


class OrderChangeStatus(BaseModel):
    id: int
    status: OrderStatus