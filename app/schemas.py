from pydantic import BaseModel
from typing import Optional

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
class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    image_url: Optional[str] = None
    category: Optional[str] = None

class ProductCreate(ProductBase):
    pass  # Dùng khi Client gửi dữ liệu lên để tạo mới

class Product(ProductBase):
    id: int

    class Config:
        from_attributes = True # Giúp chuyển đổi từ SQLAlchemy model sang Pydantic
