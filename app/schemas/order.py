from pydantic import BaseModel
from typing import List
from datetime import datetime
from app.schemas.product import Product

class OrderItemBase(BaseModel):
    product_id: int
    quantity: int
    price: float

class OrderItemResponse(OrderItemBase):
    id: int
    order_id: int
    product: Product

    class Config:
        from_attributes = True


class OrderBase(BaseModel):
    total_price: float
    status: str = "pending"

class OrderCreate(OrderBase):
    user_id: int
    items: List[OrderItemBase]

class OrderResponse(OrderBase):
    id: int
    user_id: int
    created_at: datetime
    items: List[OrderItemResponse] = []

    class Config:
        from_attributes = True