from pydantic import BaseModel, Field
from typing import Optional,List
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, DateTime
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
# --- SCHEMAS CHO GIỎ HÀNG (CART) ---

class CartBase(BaseModel):
    product_id: int
    quantity: int = 1

class CartCreate(CartBase):
    pass  # Dùng khi client gửi yêu cầu thêm vào giỏ

class CartResponse(CartBase):
    id: int
    user_id: int
    product: Product  # Trả về kèm thông tin chi tiết sản phẩm để hiện ảnh/tên

    class Config:
        from_attributes = True
# --- SCHEMAS CHO CHI TIẾT ĐƠN HÀNG (ORDER ITEM) ---

class OrderItemBase(BaseModel):
    product_id: int
    quantity: int
    price: float  # Giá tại thời điểm mua

class OrderItemResponse(OrderItemBase):
    id: int
    order_id: int
    product: Product

    class Config:
        from_attributes = True
        
# --- SCHEMAS CHO ĐƠN HÀNG (ORDER) ---

class OrderBase(BaseModel):
    total_price: float
    status: str = "pending"

class OrderCreate(OrderBase):
    user_id: int
    # Có thể thêm danh sách các item khi tạo đơn
    items: List[OrderItemBase] 

class OrderResponse(OrderBase):
    id: int
    user_id: int
    created_at: datetime
    items: List[OrderItemResponse] = [] # Trả về kèm danh sách các món đã mua

    class Config:
        from_attributes = True
class UserBase(BaseModel):
    username: str
    role: Optional[str] = "customer"

# Dùng khi Đăng ký (Client gửi username + password)
class UserCreate(UserBase):
    password: str = Field(..., min_length=6, description="Mật khẩu ít nhất 6 ký tự")

# Dùng để trả về thông tin (KHÔNG bao gồm mật khẩu để bảo mật)
class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True # Chuyển đổi từ SQLAlchemy model sang Pydantic

# Dùng khi Đăng nhập
class UserLogin(BaseModel):
    username: str
    password: str