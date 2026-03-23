from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from ..database import Base
from sqlalchemy.orm import relationship
from datetime import datetime

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    total_price = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20), default="pending")

    owner = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")