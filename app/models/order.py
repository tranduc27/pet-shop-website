from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Text
from ..database import Base
from sqlalchemy.orm import relationship
from datetime import datetime

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    session_id = Column(String(100), nullable=True, index=True)
    guest_name = Column(String(100), nullable=True)
    guest_phone = Column(String(20), nullable=True)
    guest_address = Column(Text, nullable=True)
    return_reason = Column(Text, nullable=True)
    return_image_url = Column(String(255), nullable=True)
    
    total_price = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20), default="pending")

    owner = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")