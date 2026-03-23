from pydantic import BaseModel
from typing import Optional

<<<<<<< HEAD:app/schemas/product.py
=======
# Schema cho User
class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str
    is_admin: Optional[bool] = False

class User(UserBase):
    id: int
    is_admin: bool

    class Config:
        from_attributes = True

# Schema cho Token JWT
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# Schema cho Sản phẩm
>>>>>>> 5d7198a0547d63d0a5fb9b3e73db4afdff710709:app/schemas.py
class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    image_url: Optional[str] = None
    category: Optional[str] = None

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int

    class Config:
        from_attributes = True