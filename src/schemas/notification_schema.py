from typing import Optional
from pydantic import BaseModel, Field
from models.notifications import NotificationType


class NotificationCreate(BaseModel):
    order_id: int
    type: NotificationType
    message: Optional[str] = Field(None)
