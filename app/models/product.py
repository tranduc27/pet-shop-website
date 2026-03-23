<<<<<<< HEAD:app/models/product.py
from sqlalchemy import Column, Integer, String, Float, Text
from ..database import Base
=======
from sqlalchemy import Column, Integer, String, Float, Text, Boolean
from .database import Base
>>>>>>> 5d7198a0547d63d0a5fb9b3e73db4afdff710709:app/models.py

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_admin = Column(Boolean, default=False)

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    image_url = Column(String(255))
    category = Column(String(50))
    stock = Column(Integer)