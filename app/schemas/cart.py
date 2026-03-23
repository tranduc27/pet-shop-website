from pydantic import BaseModel
from app.schemas.product import Product

class CartBase(BaseModel):
    product_id: int
    quantity: int = 1

class CartCreate(CartBase):
    pass

class CartResponse(CartBase):
    id: int
    user_id: int
    product: Product

    class Config:
        from_attributes = True