from sqlalchemy import Column, Integer, String, Float, Text, Boolean
from ..database import Base

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    image_url = Column(String(255))
    category = Column(String(50))
    pet_type = Column(String(50), nullable=True, default="Chung")
    stock = Column(Integer)
    size = Column(String(50), nullable=True)
    discount_percent = Column(Float, default=0.0)
    is_today_sale = Column(Boolean, default=False)