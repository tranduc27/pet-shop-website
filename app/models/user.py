from sqlalchemy import Column, Integer, String
from ..database import Base
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), nullable=False)
    password = Column(String(100), nullable=False)
    role = Column(String(50), default="Customer")

    orders = relationship("Order", back_populates="owner")
    carts = relationship("Cart", back_populates="user")