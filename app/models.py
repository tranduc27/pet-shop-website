from sqlalchemy import Column, Integer, String, Float, Text
from .database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    image_url = Column(String(255))  # Đường dẫn ảnh lưu trong /static/
    category = Column(String(50))    # VD: Thức ăn, Phụ kiện, Thú cảnh
